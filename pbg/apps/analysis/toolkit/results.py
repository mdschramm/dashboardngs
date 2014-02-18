from django.conf import settings
import MySQLdb


class ResultsFinder(object):
    """
    The results finder object is used for plumbing databases for results
    info. I chose to implement this functionality with classes rather than
    functions to take advantage of inheritance: every cancer needs to use
    the functions in ResultsFinder, but some may need to use them a little
    differently.
    """
    def __init__(self, project_name, sample_names, cancer_type):
        self.project_name = project_name
        self.sample_names = sample_names
        self.cancer_type = cancer_type.lower()
        self.candidate_gene_list_table = \
                self.cancer_type + "_cancer_gene_annot"
        self.candidate_variant_list_table = \
                project_name + "_candidate_variant_list"
        self.manual_review_table = \
                project_name + "_somaticMuts_manualReview"
        conn = MySQLdb.connect(\
                user=settings.DATABASES['default']['USER'],
                passwd=settings.DATABASES['default']['PASSWORD'],
                db=settings.DATABASES['default']['NAME'],
                host=settings.DATABASES['default']['HOST'])
        cur = conn.cursor()
        query = """\
                SHOW TABLES LIKE '{0}_somaticMuts_ngsPipelineResults%';\
                """.format(self.project_name)
        cur.execute(query)
        self.results_tables = [res[0] for res in cur.fetchall()]
        cur.close()
        conn.close()

    @staticmethod
    def make_link(project_name, chrom, start, end):
        # While less clear than triple-quoted strings, Python's implicit
        # string concatination does not give me any unwanted whitespace.
        link = ("http://node3.1425mad.mssm.edu/uziloa01/web/jbrowse/"
                "index.html?data=data/{0}&loc=chr{1}:{2}..{3}"
                "".format(project_name, chrom, start, end))
        return link

    @staticmethod
    def database_has_table(table_name):
        conn = MySQLdb.connect(\
                user=settings.DATABASES['default']['USER'],
                passwd=settings.DATABASES['default']['PASSWORD'],
                db=settings.DATABASES['default']['NAME'],
                host=settings.DATABASES['default']['HOST'])
        cur = conn.cursor()
        query = "SHOW TABLES LIKE '{0}';".format(table_name)
        cur.execute(query)
        res = cur.fetchone()
        cur.close()
        conn.close()
        if res:
            return True
        return False

    def has_gene_info(self):
        if not self.database_has_table("gene_boundary"):
            return False
        if not self.database_has_table(self.candidate_gene_list_table):
            return False
        return True

    def get_gene_info(self):
        if not self.has_gene_info():
            return
        conn = MySQLdb.connect(\
                user=settings.DATABASES['default']['USER'],
                passwd=settings.DATABASES['default']['PASSWORD'],
                db=settings.DATABASES['default']['NAME'],
                host=settings.DATABASES['default']['HOST'])
        cur = conn.cursor()
        query = """\
                SELECT GeneID, chr, start, end, gene_boundary.symbol,\
                source, description FROM gene_boundary, {0} WHERE\
                {0}.symbol=gene_boundary.symbol ORDER BY symbol ASC;\
                """.format(self.candidate_gene_list_table)
        cur.execute(query)
        for result in cur.fetchall():
            result = list(result)
            chrom = result[1]
            start = result[2]
            end = result[3]
            link = self.make_link(self.project_name, chrom, start, end)
            result.insert(1, link)
            yield result
        cur.close()
        conn.close()

    def has_variant_info(self):
        if self.database_has_table(self.candidate_variant_list_table):
            return True
        return False

    def get_variant_info(self):
        if not self.has_variant_info():
            return
        conn = MySQLdb.connect(\
                user=settings.DATABASES['default']['USER'],
                passwd=settings.DATABASES['default']['PASSWORD'],
                db=settings.DATABASES['default']['NAME'],
                host=settings.DATABASES['default']['HOST'])
        cur = conn.cursor()
        # Each candidate variant list table have columns with identical
        # names to the project's sample names.
        query = """\
                SELECT sample_cnt, mutation_ID, symbol, GeneID, chrom,\
                chrom_start, chrom_end, Mutation_CDS, Mutation_AA,\
                Mutation_Description, {0} FROM {1} ORDER BY sample_cnt\
                DESC LIMIT 1000;\
                """.format(", ".join(self.sample_names),
                        self.candidate_variant_list_table)
        cur.execute(query)
        for result in cur.fetchall():
            result = list(result)
            chrom = result[4]
            start = result[5]
            end = result[6]
            link = self.make_link(self.project_name, chrom, start, end)
            result.insert(1, link)
            yield result
        cur.close()
        conn.close()

    def has_tier_info(self):
        if not self.database_has_table(self.manual_review_table):
            return False
        if not self.results_tables:
            return False
        return True

    def get_tier_info(self, tier_num, results_table):
        if not self.has_tier_info():
            return
        conn = MySQLdb.connect(\
                user=settings.DATABASES['default']['USER'],
                passwd=settings.DATABASES['default']['PASSWORD'],
                db=settings.DATABASES['default']['NAME'],
                host=settings.DATABASES['default']['HOST'])
        cur = conn.cursor()
        query = """\
                SELECT {0}.id, Symbol, dbSNP, {0}.chrom, {0}.pos,\
                ref, alt, varscanSomaticStatus, pvalue, filter,\
                effect, effect_impact, functional_class, codon_change,\
                amino_acid_change, Normal, Tumor, ESP5400_freq_All,\
                1000genome_freq_ALL, source, mutationType, inRnaSeq,\
                regionAlignability, lastUpdated FROM {0} LEFT OUTER JOIN\
                {1} ON {0}.id = {1}.id WHERE {0}.tier = {2}\
                """.format(results_table, self.manual_review_table, tier_num)
        cur.execute(query)
        for result in cur.fetchall():
            result = list(result)
            chrom = result[3]
            pos = int(result[4])
            start = pos - 100
            end = pos + 100
            link = self.make_link(self.project_name, chrom, start, end)
            result.insert(1, link)
            yield result
        cur.close()
        conn.close()
