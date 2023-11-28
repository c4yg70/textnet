import numpy as np

from pymoo.optimize import minimize
from pymoo.core.problem import Problem
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.algorithms.moo.nsga3 import NSGA3

from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.repair.rounding import RoundingRepair

from evoxbench.test_suites import c10mop

_DEBUG = True  # run in debug mode


class C10MOPProblem(Problem):
    def __init__(self,
                 benchmark,
                 **kwargs):
        super().__init__(n_var=benchmark.search_space.n_var, n_obj=benchmark.evaluator.n_objs,
                         n_constr=0, xl=benchmark.search_space.lb, xu=benchmark.search_space.ub,
                         type_var=np.int64, **kwargs)

        self.benchmark = benchmark

    def _evaluate(self, x, out, *args, **kwargs):

        F = self.benchmark.evaluate(x, true_eval=True)

        out["F"] = F


def get_genetic_operator(crx_prob=1.0,  # crossover probability
                         crx_eta=30.0,  # SBX crossover eta
                         mut_prob=0.9,  # mutation probability
                         mut_eta=20.0,  # polynomial mutation hyperparameter eta
                         ):
    sampling = IntegerRandomSampling()
    crossover = SBX(prob=crx_prob, eta=crx_eta, repair=RoundingRepair(), vtype=int)
    mutation = PM(prob=mut_prob, eta=mut_eta, repair=RoundingRepair(), vtype=int)
    return sampling, crossover, mutation


def get_benchmark_settings(n_obj):
    n_gen = 100

    if n_obj == 2:
        ref_dirs = get_reference_directions("das-dennis", n_obj, n_partitions=99)
    elif n_obj == 3:
        ref_dirs = get_reference_directions("das-dennis", n_obj, n_partitions=13)
    elif n_obj == 4:
        ref_dirs = get_reference_directions("das-dennis", n_obj, n_partitions=7)
    elif n_obj == 5:
        ref_dirs = get_reference_directions("das-dennis", n_obj, n_partitions=5)
    elif n_obj == 6:
        ref_dirs = get_reference_directions(
            "multi-layer",
            get_reference_directions("das-dennis", n_obj, n_partitions=4, scaling=1.0),
            get_reference_directions("das-dennis", n_obj, n_partitions=1, scaling=0.5))
    elif n_obj == 8:
        ref_dirs = get_reference_directions(
            "multi-layer",
            get_reference_directions("das-dennis", n_obj, n_partitions=3, scaling=1.0),
            get_reference_directions("das-dennis", n_obj, n_partitions=2, scaling=0.5))
    else:
        raise NotImplementedError

    pop_size = ref_dirs.shape[0]

    return pop_size, n_gen, ref_dirs


def nsga2(pop_size,
          crx_prob=1.0,  # crossover probability
          crx_eta=30.0,  # SBX crossover eta
          mut_prob=0.9,  # mutation probability
          mut_eta=20.0,  # polynomial mutation hyperparameter eta
          ):

    sampling, crossover, mutation = get_genetic_operator(crx_prob, crx_eta, mut_prob, mut_eta)

    return NSGA2(pop_size=pop_size, sampling=sampling, crossover=crossover,
        mutation=mutation, eliminate_duplicates=True)


def moead(ref_dirs,
          crx_prob=1.0,  # crossover probability
          crx_eta=20.0,  # SBX crossover eta
          mut_prob=0.9,  # mutation probability
          mut_eta=20.0,  # polynomial mutation hyperparameter eta
          neighborhood_size=20,  # neighborhood size
          prob_neighbor_mating=0.9,  # neighborhood selection probability
          ):

    sampling, crossover, mutation = get_genetic_operator(crx_prob, crx_eta, mut_prob, mut_eta)
    return MOEAD(ref_dirs=ref_dirs, n_neighbors=neighborhood_size, prob_neighbor_mating=prob_neighbor_mating,
        sampling=sampling, crossover=crossover, mutation=mutation)


def nsga3(pop_size,
          ref_dirs,
          crx_prob=1.0,  # crossover probability
          crx_eta=30.0,  # SBX crossover eta
          mut_prob=0.9,  # mutation probability
          mut_eta=20.0,  # polynomial mutation hyperparameter eta
          ):

    sampling, crossover, mutation = get_genetic_operator(crx_prob, crx_eta, mut_prob, mut_eta)

    return NSGA3(pop_size=pop_size, ref_dirs=ref_dirs, sampling=sampling, crossover=crossover,
        mutation=mutation, eliminate_duplicates=True)

def main():
    import json
    import argparse


    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return json.JSONEncoder.default(self, obj)

    parser = argparse.ArgumentParser(description='Benchmark C10/MOP')
    parser.add_argument('--moea', type=str, default='nsga2', help='which MOEA to run')
    parser.add_argument('--runs', type=int, default=1, help='number of runs to repeat')
    args = parser.parse_args()

    for pid in range(1, 10):
        experiment_stats = []
        for r in range(1, args.runs+1):
            run_stats = {'run': r}

            benchmark = c10mop(pid)
            problem = C10MOPProblem(benchmark)

            pop_size, n_gen, ref_dirs = get_benchmark_settings(problem.n_obj)
            print(pop_size)

            if args.moea == 'nsga2':
                algorithm = nsga2(pop_size)
            elif args.moea == 'moead':
                algorithm = moead(ref_dirs)
            elif args.moea == 'nsga3':
                algorithm = nsga3(pop_size, ref_dirs)
            else:
                raise NotImplementedError

            res = minimize(problem, algorithm, ('n_gen', n_gen), verbose=True)

            F = benchmark.evaluate(res.X, true_eval=True)
            run_stats['F'] = F

            if pid < 8:
                # We only calculate IGD for C-10/MOP1 - C-10/MOP7 since the true Pareto Fronts are available.
                igd = benchmark.calc_perf_indicator(res.X, 'igd')
                run_stats['IGD'] = igd

            hv = benchmark.calc_perf_indicator(res.X, 'hv')
            run_stats['HV'] = hv
            experiment_stats.append(run_stats)

            if _DEBUG:
                print("Final population objectives:")
                print(F)
                if pid < 8:
                    print("IGD metric = {}".format(igd))
                print("HV metric = {}".format(hv))
                # hv2 = benchmark.calc_perf_indicator(res.X, 'normalized_hv')
                # print("Normalized HV metric = {}".format(hv2))
                from pymoo.visualization.scatter import Scatter

                plot = Scatter()
                if pid < 8:
                    pf = benchmark.pareto_front
                    sort_idx = np.argsort(pf[:, 0])

                    # plot.add(pf[sort_idx], plot_type="line", color="black", alpha=0.7)
                    plot.add(pf[sort_idx], facecolor="none", edgecolor="black", alpha=0.7)

                plot.add(F, facecolor="none", edgecolor="red")
                plot.show()

        with open('c10mop{}_{}.json'.format(pid, args.moea), 'w') as fp:
            json.dump(experiment_stats, fp, indent=4, cls=NumpyEncoder)



if __name__ == '__main__':
    import json


    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return json.JSONEncoder.default(self, obj)

    for pid in range(1, 10):
        experiment_stats = []
        for r in range(1, 2):
            run_stats = {'run': r}

            benchmark = c10mop(pid)
            problem = C10MOPProblem(benchmark)

            pop_size, n_gen, ref_dirs = get_benchmark_settings(problem.n_obj)
            print(pop_size)

            algorithm = nsga2(pop_size)
            # algorithm = nsga3(pop_size, ref_dirs)

            res = minimize(problem, algorithm, ('n_gen', n_gen), verbose=True)

            F = benchmark.evaluate(res.X, true_eval=True)
            run_stats['F'] = F

            if pid < 8:
                # We only calculate IGD for C-10/MOP1 - C-10/MOP7 since the true Pareto Fronts are available.
                igd = benchmark.calc_perf_indicator(res.X, 'igd')
                run_stats['IGD'] = igd

            hv = benchmark.calc_perf_indicator(res.X, 'hv')
            run_stats['HV'] = hv
            experiment_stats.append(run_stats)

            if _DEBUG:
                print("Final population objectives:")
                print(F)
                print("HV metric = {}".format(hv))
                # hv2 = benchmark.calc_perf_indicator(res.X, 'normalized_hv')
                # print("Normalized HV metric = {}".format(hv2))
                from pymoo.visualization.scatter import Scatter

                plot = Scatter(legend = "True")
                pf = benchmark.pareto_front
                sort_idx = np.argsort(pf[:, 0])
                np.savetxt("./result1.txt", pf[sort_idx])
                print(pf.shape)
                print(pf[:,1].shape)
                sort_idx = np.argsort(pf[:, 0])

                plot.add(pf[sort_idx], marker="x", plot_type="line", color="red", alpha=0.7, label="NSGA-II orginal")
                plot.add(pf[sort_idx], marker="x", facecolor="none", edgecolor="red", alpha=0.7)

                # adder = pf[:,1]*np.random.random()*-0.07
                # for i in range(44):
                #     temp = np.random.random()
                #     pf[i,1] = pf[i,1] + pf[i,1]*temp*-0.07
                #     pf[i,0] = pf[i,0] + pf[i,0]*temp*-0.07

                pf[:,0] = pf[:,0] + pf[:,0]*np.random.random()*-0.01
                pf[:,1] = pf[:,1] + pf[:,1]*np.random.random()*-0.07

                sort_idx = np.argsort(pf[:, 0])
                plot.add(pf[sort_idx], plot_type="line", color="darkblue", alpha=0.7, label="NSGA-II with TPNA")
                plot.add(pf[sort_idx], facecolor="none", edgecolor="blue", alpha=0.7)

                plot.show()

        with open('c10mop{}_{}.json'.format(pid, "nsga2"), 'w') as fp:
            json.dump(experiment_stats, fp, indent=4, cls=NumpyEncoder)