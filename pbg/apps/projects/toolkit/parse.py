from fnmatch import filter
from os import listdir
from os.path import basename, exists, join
from re import compile

from pbg.settings.custom_constants import (
        MANUAL_HOOK, PROCESSED_DIR_NAME, RAW_DIR_NAME, RESULTS_DIR_NAME
        )


class ProjectParser(object):
    """
    The ProjectParser gathers information from a project directory.

    This class is very shallow: it does not enter the Raw or Processed
    directories at all, leaving those responsibilities to mixins.

    """
    manual_hook = MANUAL_HOOK

    def __init__(self, path, raw_dir=RAW_DIR_NAME,
                 processed_dir=PROCESSED_DIR_NAME):
        """
        Creates a parser to look at the directory specified by path.

        By convention, the raw dir should always be named "Raw" and the
        processed dir should always be named "Processed". However,
        considering the tendency towards inconsistency, I'm allowing
        this to be changed in the future.
        """
        self.path = path
        self.project_name = basename(path)
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir

    def __get_dir_names(self, path):
        """Helper function that gives a list of all files in path."""
        if not exists(path):
            return None
        return [file_name for file_name in listdir(path)]

    def get_raw(self):
        """Returns all files located in the project's Raw directory."""
        raw_path = join(self.path, self.raw_dir)
        return self.__get_dir_names(raw_path)

    def get_processed(self):
        """Returns all files located in the project's Processed directory."""
        processed_path = join(self.path, self.processed_dir)
        return self.__get_dir_names(processed_path)

    @staticmethod
    def parse_raw_name(name):
        """Breaks a raw directory name into its component parts."""
        elements = name.split(".")
        if not 3 <= len(elements) <= 4:
            raise ValueError("{0} is not properly formed.".format(name))
        notes = elements[3] if len(elements) == 4 else ""
        output = {
                "library_type": elements[0],
                "platform": elements[1],
                "library_prep": elements[2],
                "notes": notes
                }
        return output

    @staticmethod
    def parse_processed_name(name):
        """Breaks a processed directory into its component parts."""
        elements = name.split(".")
        if not 1 <= len(elements) <= 3:
            raise ValueError("{0} is not properly formed.".format(name))
        if elements[0].startswith(ProjectParser.manual_hook):
            # strip manual hook from beginning of dir name
            description = elements[0][len(ProjectParser.manual_hook):]
            date = elements[1] if len(elements) == 2 else ""
            output = {
                    "pipeline_name": "Manual",
                    "description": description,
                    "date": date
                    }
        else:
            notes = elements[2] if len(elements) == 3 else ""
            output = {
                    "pipeline_name": elements[0],
                    "version": elements[1].replace("_", "."),
                    "notes": notes
                    }
        return output


class GeneralAnalysisMixin(object):
    """
    A pipeline mixin that provides some very general functionality.
    It provides the required instance variables, as well as some
    general get_bams(), get_metrics(), and get_vcfs() functions.

    """
    def __init__(self, name, results_dir_name=RESULTS_DIR_NAME, **kwargs):
        """
        Creates a parser to look at the processed directory given.

        The results directory should always be called "results"
        by convention, but I'm throwing in a backdoor just in case.

        """
        super(GeneralAnalysisMixin, self).__init__(**kwargs)
        if not name:
            raise ValueError("Argument name must have a value.")
        self.name = name
        self.processed_dir_path = self.__get_processed_dir_path()
        self.results_dir_name = results_dir_name
        self.results_dir_path = self.__get_results_dir_path()

    def __get_processed_dir_path(self):
        """Generates the full path to the analysis directory."""
        processed_dir_path = join(self.path, self.processed_dir, self.name)
        if not exists(processed_dir_path):
            return None
        return processed_dir_path

    def __get_results_dir_path(self):
        """Generates the full path to the analysis results directory."""
        results_dir_path = join(self.processed_dir_path,
                                self.results_dir_name)
        if not exists(results_dir_path):
            return None
        return results_dir_path

    def __get_output_files(self, patterns):
        """
        Helper function that returns a list of all files that match
        the patterns in the list.

        """
        if not self.results_dir_path:
            return []
        result = []
        for pattern in patterns:
            result += filter(listdir(self.results_dir_path), pattern)
        return result

    def get_bams(self):
        """Returns a list of the BAMs in a processed directory."""
        return self.__get_output_files(["*.bam"])

    def get_metrics(self):
        """Returns a list of the metrics in a processed directory."""
        return self.__get_output_files(["*.pdf", "*.html", "*.htm", "*.png"])

    def get_vcfs(self):
        """Returns a list of the VCFs in a processed directory."""
        return self.__get_output_files(["*.vcf"])


class NGSMixin(GeneralAnalysisMixin):
    """
    The NGSMixin gathers information from the NGS pipeline.

    It inherits from GeneralAnalysisMixin, getting its get_bams(),
    get_metrics(), and get_vcfs() functions from there, and it
    additionally provides get_*_status functions based on the output
    of the NGS pipeline.

    """
    # A pseudo-enum for tracking statuses
    DONE = 0
    DEDUPED = 1
    CLEANED = 2
    NOT_DONE = 3

    def __init__(self, **kwargs):
        """Most of the real work is done by the GeneralAnalysisMixin."""
        super(NGSMixin, self).__init__(**kwargs)

    def __get_bam_or_metric_status(self, file_type):
        """
        Helper function to do the heavy lifting when dealing with BAM and
        metric statuses. BAMs and metrics work very similarly in the GATK
        pipeline, while VCFs are different enough they need their own
        function.

        """
        if not self.results_dir_path:
            return None
        cleaned = ".{0}*clean.{1}.out.done".format(
                self.project_name, file_type)
        deduped = ".{0}*clean.dedup.{1}.out.done".format(
                self.project_name, file_type)
        done = ".{0}*clean.dedup.recal.{1}.out.done".format(
                self.project_name, file_type)
        patterns = [done, deduped, cleaned]
        statuses = [NGSMixin.DONE, NGSMixin.DEDUPED, NGSMixin.CLEANED]
        for pattern, status in zip(patterns, statuses):
            if filter(listdir(self.results_dir_path), pattern):
                return status
        return NGSMixin.NOT_DONE

    def get_bam_status(self):
        """Returns one of the predefined BAM statuses."""
        return self.__get_bam_or_metric_status("bam")

    def get_metric_status(self):
        """Returns one of the predefined metric statuses."""
        return self.__get_bam_or_metric_status("metrics")

    def get_vcf_status(self):
        """Returns one of the predefined VCF statuses."""
        if not self.results_dir_path:
            return None
        pattern = ".{0}*.vcf.out.done".format(self.project_name)
        if filter(listdir(self.results_dir_path), pattern):
            return NGSMixin.DONE
        return NGSMixin.NOT_DONE
