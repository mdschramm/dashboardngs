from xml.etree import ElementTree
from os import listdir
from os.path import join
from fnmatch import filter


class CancerMixin(object):
    """A study type mixin with functions to get cancer-related info."""
    def __init__(self, **kwargs):
        super(CancerMixin, self).__init__(**kwargs)

    def get_xml_file(self):
        """
        Returns the xml file in the directory, or None if there is
        not exactly one file there.

        """
        pattern = "*.xml"
        xml_files = filter(listdir(self.processed_dir_path), pattern)
        if not xml_files or len(xml_files) > 1:
            return None
        return xml_files[0]    # Only element

    def get_xml_info(self):
        """
        Returns a dictionary containing information found in the XML file.

        {
            "sample_name": {
                "tumor": True/False,
                "purity": decimal/None
            },
            ...
        }

        """
        xml_file = self.get_xml_file()
        if not xml_file:
            return None
        xml_path = join(self.processed_dir_path, xml_file)
        res = {}
        tree = ElementTree.parse(xml_path)
        cohort = tree.getroot()
        for fastq in cohort.findall("fastq"):
            if "sample" in fastq.attrib and fastq.attrib["sample"] not in res:
                sample_name = fastq.attrib["sample"]
                res[sample_name] = {}
                if "purity" in fastq.attrib:
                    res[sample_name]["tumor"] = True
                    res[sample_name]["purity"] = float(fastq.attrib["purity"])
                else:
                    res[sample_name]["tumor"] = False
                    res[sample_name]["purity"] = None
        return res
