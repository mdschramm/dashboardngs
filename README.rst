====================
Multiscale Dashboard
====================

The majority of this project was built by Mark Micchelli, a full-time employee at 
Mt. Sinai whom I worked with. This is the version of the dashboard when I left Mt. 
Sinai. The project was originally remotely stored on bitbucket.org, so I moved it here
As an intern, I coded and contributed to the following files:

dashboardngs/pbg/apps/analysis/forms.py 
dashboardngs/pbg/apps/analysis/models.py
dashboardngs/pbg/apps/analysis/views.py

dashboardngs/pbg/apps/analysis/static/analysis.js
dashboardngs/pbg/apps/analysis/static/geneform.js
dashboardngs/pbg/apps/analysis/static/resultsTable.js

dashboardngs/pbg/apps/analysis/templates/minitable_bam.html
dashboardngs/pbg/apps/analysis/templates/minitable_fastq.html
dashboardngs/pbg/apps/analysis/templates/minitable_metric.html
dashboardngs/pbg/apps/analysis/templates/minitable_pathology.html
dashboardngs/pbg/apps/analysis/templates/minitable_sequencing.html
dashboardngs/pbg/apps/analysis/templates/minitable_vcf.html
dashboardngs/pbg/apps/analysis/templates/project_detail.html
dashboardngs/pbg/apps/analysis/templates/project_list.html

dashboardngs/pbg/static/table.css



Here is a brief breakdown of the files in the repo:

* dashboardngstests/

  * A directory used for testing directory-parsing scripts in the pbg test suite.

* docs/
  
  * Documentation for the Multiscale Dashboard

* old/
  
  * The old version of the Multiscale Dashboard, namely AutoBot.pl and
    ProjectSettings.txt. This is included here for reference, and will
    eventually be deleted.

* pbg/

  * The central Django project for the Multiscale Dashboard

* perfectum_dashboard/
  
  * The original, unmodified code that came with the Perfectum Dashboard
    Bootstrap template

* requirements.txt
  
  * All the third-party packages needed for this project

* vcfviewer/
  
  * I'm not sure how this got here or what it is.
