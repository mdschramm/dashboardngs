#!/usr/bin/env python
import os.path
import os
import re


def get_qc_path(sample_name, sequencing_type="RNA", base_path=""):
    """
    Returns the full path of the RNA QC directory. Right now it's
    pretty much hard-coded :P
    """
    if not base_path:
        base_path = ("/projects/GCF/outgoing/InstituteProjects/"
                     "CancerSequencing/RNA_analysis/tophat209_QC.2.2")
    # ugly hack around inconsistant naming conventions (namely,
    # "PID4596_13006_Tumor" instead of simply "PID4596_Tumor")
    sample_name_elements = sample_name.split("_")
    sample_name = ".*".join(sample_name_elements)
    pat = re.compile(r"^QC_{0}.*_{1}$".format(sample_name, sequencing_type))
    for dir_name in os.listdir(base_path):
        full_path = os.path.join(base_path, dir_name)
        if os.path.isdir(full_path):
            m = pat.match(dir_name)
            if m:
                return full_path
    raise IOError("qc_path does not exist")


def get_index(qc_path):
    """
    Returns the string "index.html" if it exists in the qc_path directory,
    and raises an IOError if it does not.
    """
    file_name = "index.html"
    full_path = os.path.join(qc_path, file_name)
    if not os.path.exists(full_path):
        raise IOError(file_name + " does not exist")
    return file_name


def get_three_prime_bias(qc_path):
    """
    Returns a dictionary that looks like this:
    {
        "txt":"meanCoverage_medium.txt",
        "png":"meanCoverage_medium.png",
    }
    If either of those files do not exist the directory specified
    by qc_path, raises an IOError.
    """
    three_prime_bias = "meanCoverage_medium"
    file_types = ("txt", "png")
    res = {}
    for file_type in file_types:
        file_name = three_prime_bias + "." + file_type
        full_path = os.path.join(qc_path, file_name)
        if not os.path.exists(full_path):
            raise IOError(file_name + " does not exist")
        res[file_type] = file_name
    return res


def get_metrics(sample_name, sequencing_type="RNA", base_path=""):
    """
    Returns a dictionary containing a sample's QC path, index.html
    file, and 3' bias files. This function doesn't quite follow
    best practices regarding exception handling, but I like the
    concision.
    """
    try:
        qc_path = get_qc_path(sample_name, sequencing_type, base_path)
        index_file = get_index(qc_path)
        three_prime = get_three_prime_bias(qc_path)
    except IOError:
        return None
    else:
        return {"path":qc_path, "index":index_file, "three_prime":three_prime}
