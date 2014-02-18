import fnmatch
import os
import re
import xml.etree.ElementTree
from xml.parsers.expat import ExpatError


class MultipleXMLFilesFoundException(Exception):
    pass


def find_xml_file(project_dir_path):
    """
    Returns the name of a project's XML file. If it finds
    more than one, it throws a MultipleXMLFilesFoundException.
    """
    files = fnmatch.filter(os.listdir(project_dir_path), "*.xml")
    if len(files) > 1:
        raise MultipleXMLFilesFoundException("Multiple XML files found in %s"
                % project_dir_path)
    elif len(files) == 0:
        return None
    return files[0] # only element


def find_makefile(project_dir_path):
    """
    Returns the name of a project's Makefile, if it can find one. This
    result will be either 'GNUMakefile', 'makefile', or 'Makefile'. If
    none of those files exist, it returns None.
    """
    possible_names = ["GNUMakefile", "makefile", "Makefile"]
    for possible_name in possible_names:
        # using this instead of os.path.exists because of Mac case-
        # insensitivity bug
        if possible_name in os.listdir(project_dir_path):
            break
    else:
        return None
    return possible_name


def find_results_directory(project_dir_path, makefile):
    """
    Returns the name of the results directory of a project. It first
    tries to find the results directory name from the project's makefile,
    then it looks for a directory called 'results', and if that all
    fails, it returns None.
    """
    makefile_path = os.path.join(project_dir_path, makefile)
    if not os.path.exists(makefile_path):
        raise IOError("{0} does not exist".format(makefile_path))
    regex = re.compile(r"^OUT_DIR=(.*)$")
    with open(makefile_path) as f:
        for line in f:
            m = regex.match(line)
            if m:
                results_dir = m.group(1)
                break
        else:
            results_dir = "results"
    results_dir_path = os.path.join(project_dir_path, results_dir)
    if not os.path.exists(results_dir_path):
        return None
    return results_dir


class ProjectNameNotInMakefileException(Exception):
    pass


def get_project_name(project_dir_path, makefile):
    """
    Returns the name of the project in the directory. Discovers this
    information by parsing the project's Makefile.
    """
    makefile_path = os.path.join(project_dir_path, makefile)
    if not os.path.exists(makefile_path):
        raise IOError("{0} does not exist".format(makefile_path))
    regex = re.compile(r"^PROJECT=(.*)$")
    with open(makefile_path) as f:
        for line in f:
            m = regex.match(line)
            if m:
                project_name = m.group(1)
                break
        else:
            raise ProjectNameNotInMakefileException
    return project_name


class ImproperlyFormattedXMLFileException(Exception):
    pass


def get_sample_names(project_dir_path, xml_file):
    """
    Returns the sample names of project by parsing through the given
    XML file.
    """
    xml_file_path = os.path.join(project_dir_path, xml_file)
    try:
        tree = xml.etree.ElementTree.parse(xml_file_path)
    except ExpatError: # Python 2.6
        raise ImproperlyFormattedXMLFileException()
    except xml.etree.ElementTree.ParseError: # Python 2.7
        raise ImproperlyFormattedXMLFileException()
    root = tree.getroot()
    samples = set()
    for fastq in root: # fastq is immediate child of the root (i.e. cohort)
        sample_name = fastq.get("sample")
        if sample_name:
            samples.add(sample_name)
    return list(samples)


def _is_done(results_dir_path, project_name, file_type):
    if file_type == "bam" or file_type == "metrics":
        if fnmatch.filter(os.listdir(results_dir_path),
                ".{0}.*.clean.dedup.recal.{1}*.done".format(project_name,
                file_type)):
            return True
        return False
    else:
        if fnmatch.filter(os.listdir(results_dir_path),
                ".{0}.*.vcf*.done".format(project_name)):
            return True
        return False


def is_bam_done(results_dir_path, project_name):
    return _is_done(results_dir_path, project_name, "bam")


def is_metric_done(results_dir_path, project_name):
    return _is_done(results_dir_path, project_name, "metrics")


def is_vcf_done(results_dir_path, project_name):
    return _is_done(results_dir_path, project_name, "vcf")


def _get_status(results_dir_path, project_name, sample_name, file_type):
    """
    Looks at the pattern of 'clean.dedup.recal' to return a
    pretty-printed represention of the status of the given file
    type (options are 'bam' or 'metrics').
    """
    if file_type != "bam" and file_type != "metrics":
        raise ValueError("Argument 'file_type' must be 'bam' or 'metrics'.")
    cleaned = ".{0}.{1}.clean.{2}.out.done".format(project_name, sample_name,
            file_type)
    deduped = ".{0}.{1}.clean.dedup.{2}.out.done".format(project_name,
            sample_name, file_type)
    done = ".{0}.{1}.clean.dedup.recal.{2}.out.done".format(project_name,
            sample_name, file_type)
    if os.path.exists(os.path.join(results_dir_path, done)):
        return "Done."
    if os.path.exists(os.path.join(results_dir_path, deduped)):
        return "De-duped, not yet recalibrated."
    if os.path.exists(os.path.join(results_dir_path, cleaned)):
        return "Cleaned, not yet de-duped."
    return "Not yet cleaned."


def get_bam_status(results_dir_path, project_name, sample_name):
    return _get_status(results_dir_path, project_name, sample_name, "bam")


def get_metric_status(results_dir_path, project_name, sample_name):
    return _get_status(results_dir_path, project_name, sample_name, "metrics")


def get_vcf_status(results_dir_path, project_name, sample_name):
    if fnmatch.filter(os.listdir(results_dir_path),
            ".{0}.{1}.*.vcf.out.done".format(project_name, sample_name)):
        return "Done."
    return "Not done."

def get_project_vcf_status(results_dir_path, project_name):
    if fnmatch.filter(os.listdir(results_dir_path),
            ".{0}.*.vcf.out.done".format(project_name)):
        return "Done."
    return "Not done."


def get_bams(results_dir_path, project_name, sample_names):
    """
    Returns a dictionary of BAM files. The keys are sample names, and
    the values is the associated BAM file.
    """
    results = {}
    regex = re.compile(r"^{0}.(\w+?)\..*\.bam$".format(project_name))
    for file_name in os.listdir(results_dir_path):
        m = regex.match(file_name)
        if m:
            sample_name = m.group(1)
            if sample_name in sample_names:
                results[sample_name] = file_name
            else:
                pass # probably should be an exception
    return results


def get_metrics(results_dir_path, project_name, sample_names):
    results = {project_name:[], "samples":{}}
    for sample_name in sample_names:
        results["samples"][sample_name] = []
    valid_file_types = ["pdf", "html", "htm"]
    for file_type in valid_file_types:
        regex = re.compile(r"^{0}\.(\w+?)\..*\.{1}$".format(project_name,
            file_type))
        for file_name in os.listdir(results_dir_path):
            m = regex.match(file_name)
            if m:
                sample_name = m.group(1)
                if sample_name in sample_names:
                    results["samples"][sample_name].append(file_name)
                else:
                    results[project_name].append(file_name)
    return results


def get_vcfs(results_dir_path, project_name, sample_names):
    results = {project_name:[], "samples":{}}
    for sample_name in sample_names:
        results["samples"][sample_name] = []
    regex = re.compile(r"^{0}\.(\w+?)\..*vcf$".format(project_name))
    for file_name in os.listdir(results_dir_path):
        m = regex.match(file_name)
        if m:
            sample_name = m.group(1)
            if sample_name in sample_names:
                results["samples"][sample_name].append(file_name)
            else:
                results[project_name].append(file_name)
    return results
