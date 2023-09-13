import time

from algorithms import *
from default_constants import *


class SignalData(object):
    def __init__(self,
                 time,
                 signal,
                 truth_data=None,

                 # filter_alg=lp_filter_iir,
                 filter=lp_filter_iir_extracted,
                 discriminator=cfd,
                 zero_detector_alg=zero_detector2,
                 run_second_filter=False,
                 run_discriminator_twice=False,

                 slice_start=0,
                 slice_end=None,  # None sends the slice to the end
                 amp_power=16,
                 filter_args={
                     "decay_part": DECAY_PART,
                     "window_width": WINDOW_WIDTH,
                     "alpha": ALPHA,
                 },
                 # decay_part=DECAY_PART,
                 delay_samples=DELAY_SAMPLES,
                 inv_frac=INV_FRAC,

                 tolerance=TOLERANCE,
                 section_time=SECTION_TIME,
                 ):
        self.output = None
        self.sig_fil3 = None
        self.sig_cfd2 = None
        self.sig_fil2 = None
        self.sig_cfd1 = None
        self.sig_fil1 = None
        self.sig_amp = None
        self.truth_data = None
        self.sig = None
        self.t = None
        self.all_t = np.array(time)
        self.all_sig = np.array(signal)
        if len(time) != len(signal):
            raise IndexError(f"time and signal length mismatch: {len(time)} and {len(signal)}")

        self.filter = filter
        self.cfd = discriminator
        self.zd = zero_detector_alg
        self.run_second_filter = run_second_filter
        self.run_discriminator_twice = run_discriminator_twice

        if truth_data is not None:
            if len(time) != len(truth_data):
                raise IndexError(f"signal and truth_data length mismatch: {len(signal)} and {len(truth_data)}")
            self.all_truth_data = np.array(truth_data)
        else:
            self.all_truth_data = np.zeros_like(self.all_t)

        if slice_end is None:
            slice_end = len(time) - 1
        self.slice_end = slice_end

        self.all_computed_performances = []

        self.slice_start = slice_start
        self.slice_end = slice_end

        self.filter_args = filter_args
        self.delay_samples = delay_samples
        self.inv_frac = inv_frac
        self.amp_power = amp_power
        self.tolerance = tolerance
        self.section_time = section_time
        self.sampling_period = self.all_t[1] - self.all_t[0]  # Assumes constant sample time-spacing

        self.regenerate()

    def __len__(self):
        return self.slice_end - self.slice_start

    def regenerate(self):
        self.slice()
        self.run_amp()
        self.run_fil1()
        self.run_cfd1()
        if self.run_second_filter:
            self.run_fil2()
        if self.run_discriminator_twice:
            self.run_cfd2()
            self.run_fil3()
        self.run_zd()

    def slice(self):
        """Note that this affects computation as the preceding calculations aren't taken into account."""
        self.t = self.all_t[self.slice_start:self.slice_end]
        self.sig = self.all_sig[self.slice_start:self.slice_end]
        self.truth_data = self.all_truth_data[self.slice_start:self.slice_end]

    def run_amp(self):
        self.sig_amp = (self.sig * (2 ** self.amp_power)).astype(int)
        return self.sig_amp

    def run_fil1(self):
        filtered = self.filter(self.sig_amp, **self.filter_args)
        self.sig_fil1 = np.array(list(filtered))
        return self.sig_fil1

    def run_cfd1(self):
        cfd_done = self.cfd(self.sig_fil1, inv_frac=self.inv_frac, delay_samples=self.delay_samples, )
        self.sig_cfd1 = np.array(list(cfd_done))
        return self.sig_cfd1

    def run_fil2(self):
        filtered = self.filter(self.sig_cfd1, **self.filter_args)
        self.sig_fil2 = np.array(list(filtered))
        return self.sig_fil2

    def run_cfd2(self):
        cfd_done = self.cfd(self.sig_fil2, inv_frac=self.inv_frac, delay_samples=self.delay_samples, )
        self.sig_cfd2 = np.array(list(cfd_done))
        return self.sig_cfd2

    def run_fil3(self):
        filtered = self.filter(self.sig_cfd2, **self.filter_args)
        self.sig_fil3 = np.array(list(filtered))
        return self.sig_fil3

    def run_zd(self):
        if self.run_discriminator_twice:
            zd_done = self.zd(self.sig_fil3)
        elif self.run_second_filter:
            zd_done = self.zd(self.sig_fil2)
        else:
            zd_done = self.zd(self.sig_cfd1)
        self.output = np.array(list(zd_done))
        return self.output

    def set_truth_data(self, truth_data):
        self.truth_data = truth_data
        self.slice()

    def get_current_performance(self, tolerance=None, output_to_analyse=None, verbose=False):
        """
        If output_to_analyse is None, use self.output. This is so that get_performance_parallel() can
        run without changing instance variables and affecting other processes.
        --- make this a class method?
        """
        self.tolerance = tolerance or self.tolerance
        if output_to_analyse is None:
            output_to_analyse = self.output

        test_parameters = {}

        tolerance_samples = int(self.tolerance / self.sampling_period)

        total_signals, hits = compare_data_to_success_condition(output_to_analyse, self.truth_data,
                                                                tolerance_samples=tolerance_samples)
        total_triggers, misfires_complement = compare_data_to_success_condition(self.truth_data, output_to_analyse,
                                                                                tolerance_samples=tolerance_samples)

        misfires = total_triggers - misfires_complement

        if total_signals == 0:
            hitrate = None
        else:
            hitrate = hits / total_signals

        if total_triggers == 0:
            misfire_rate = None
        else:
            misfire_rate = misfires / total_triggers

        if verbose:
            print("self.delay_samples:", self.delay_samples)
            print("self.inv_frac:", self.inv_frac)
            print("tolerance:", self.tolerance)
            print("tolerance_samples:", tolerance_samples)
            print("total_signals:", total_signals)
            print("total_triggers:", total_triggers)
            print("hits:", hits)
            print("misfires:", misfires)
            print("misfire_rate:", misfire_rate)  # Possible misleading statistic
            print()

        # Record test parameters and outputs
        test_parameters["delay_samples"] = self.delay_samples
        test_parameters["inv_frac"] = self.inv_frac
        test_parameters["tolerance"] = self.tolerance
        test_parameters["tolerance_samples"] = tolerance_samples
        test_parameters["total_signals"] = total_signals
        test_parameters["total_triggers"] = total_triggers
        test_parameters["hits"] = hits
        test_parameters["hitrate"] = hitrate
        test_parameters["misfires"] = misfires
        test_parameters["misfire_rate"] = misfire_rate

        return test_parameters

    # @njit
    def get_performance(self, inv_frac_vals, delay_samples_vals, tolerance=None, verbose=False):
        self.tolerance = tolerance or self.tolerance
        if verbose:
            start_wall = time.time()
            start_cpu = time.process_time()
        all_performances = []

        if verbose: print("." * len(delay_samples_vals))
        for delay_samples in delay_samples_vals:
            self.delay_samples = delay_samples
            for inv_frac in inv_frac_vals:
                self.inv_frac = inv_frac
                self.regenerate()
                all_performances.append(self.get_current_performance(tolerance=self.tolerance))
            if verbose: print(".", end="")

        if verbose:
            end_wall = time.time()
            end_cpu = time.process_time()
            print()
            print("Wall time:", human_time(end_wall - start_wall))
            print("CPU time:", human_time(end_cpu - start_cpu))

        return all_performances

    def get_sensitivity_specificity_v1(self, tolerance=None):
        self.tolerance = tolerance or self.tolerance

        return get_sensitivity_specificity_compiled_v1(self.output, self.truth_data,
                                                       section_time=self.section_time,
                                                       sampling_period=self.sampling_period,
                                                       tolerance=self.tolerance, )

    def get_roc_curve_data(self, inv_frac_vals, delay_samples_vals, tolerance=None, verbose=False):
        self.tolerance = tolerance or self.tolerance
        all_performances = []
        if verbose:
            print("Tolerance [s]:", self.tolerance)
            start_wall = time.time()
            start_cpu = time.process_time()
            print("." * len(delay_samples_vals))
        for delay_samples in delay_samples_vals:
            self.delay_samples = delay_samples
            for inv_frac in inv_frac_vals:
                self.inv_frac = inv_frac
                self.regenerate()
                sensitivity, specificity = self.get_sensitivity_specificity_v1(tolerance=self.tolerance)
                all_performances.append({"sensitivity": sensitivity,
                                         "specificity": specificity,
                                         "inv_frac": inv_frac,
                                         "delay_samples": delay_samples,
                                         })
            if verbose: print(".", end="")

        if verbose:
            end_wall = time.time()
            end_cpu = time.process_time()
            print()
            print("Wall time:", human_time(end_wall - start_wall))
            print("CPU time:", human_time(end_cpu - start_cpu))

        return all_performances

    def get_roc_curve_data2(self, filter_arg_range, inv_frac_range, delay_samples_range,
                            filter=lp_filter_iir_extracted, filter_arg_name="decay_part",
                            tolerance=None, verbose=False):
        """ Generate ROC curve data for varied values for the first filter arg, inv_frac, delay_samples.
        For the values, takes tuple (min, max, step).
        """
        self.tolerance = tolerance or self.tolerance
        self.filter = filter

        filter_arg_vals = np.arange(*filter_arg_range)
        inv_frac_vals = np.arange(*inv_frac_range)
        delay_samples_vals = np.arange(*delay_samples_range)

        roc_datas = []
        if verbose:
            print("Tolerance [s]:", self.tolerance)
            start_wall = time.time()
            start_cpu = time.process_time()
            print("." * len(filter_arg_vals))
        for filter_arg in filter_arg_vals:
            self.filter_args[filter_arg_name] = filter_arg
            roc_data = self.get_roc_curve_data(
                inv_frac_vals=inv_frac_vals,
                delay_samples_vals=delay_samples_vals,
                tolerance=1,
                # verbose=True,
            )
            for performance in roc_data:
                performance[filter_arg_name] = filter_arg
            roc_datas.append(roc_data)
            if verbose: print(".", end="")

        if verbose:
            end_wall = time.time()
            end_cpu = time.process_time()
            print()
            print("Wall time:", human_time(end_wall - start_wall))
            print("CPU time:", human_time(end_cpu - start_cpu))

        roc_datas_flat = [item for row in roc_datas for item in row]
        return roc_datas_flat
