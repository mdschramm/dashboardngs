#!/usr/bin/perl
use strict;
use CGI;
use lib("JSON-2.59/lib","/projects/GCF/scripts");
use JSON qw( );
use common_util::generic::myUtil;

print "Content-type:text/html\n\n";

my %flavor;

$flavor{1}=",Tumor,Normal|WES,WGS,E+G,RNA";
#$flavor{1}{cols}="WES,WGS,RNA";
$flavor{2}=",Primary,Recurring,Normal|WES,RNA";
$flavor{3}=",S1_Tumor,S2_Tumor,Blood|WES,RNA";
$flavor{4}=",Primary,Normal|WES,RNA";
$flavor{5}=",Tumor,Normal|E+G,RNA";
#$flavor{2}{cols}="WES,RNA";


my %projects;

=pod
CancerSeq,PID4596_13006,WES{Tumor:Normal}|WGS{Tumor:Normal}|RNA{Tumor}
Ovarian,PT165,WES{Primar:Recurrent:Blood}|RNA{Primary:Recurrent}
=cut

open(IN,"ProjectSettings.txt") or printError("Cant open project settings file");

while(my $line=<IN>){
	chomp($line);
	if($line=~m/#/){next;}
	my @cols=split(':',$line);
	$projects{$cols[1]}{type}="$cols[0]";
	$projects{$cols[1]}{settings}="$cols[2]";
	$projects{$cols[1]}{path}="$cols[-1]";
}
my $myUtil=common_util::generic::myUtil->new();

print_header();
print_RightMenu();
print_Pane();

exit;

sub print_header {
	print qq{<!DOCTYPE html>
<html lang="en">
<head>
	
	<!-- start: Meta -->
	<meta charset="utf-8">
	<title>Cancer Sequencing Project Dashboard</title>
	<meta name="description" content="Cancer Sequencing Project Dashboard">
	<meta name="author" content="Hardik Shah">
	<!-- end: Meta -->
	
	<!-- start: Mobile Specific -->
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<!-- end: Mobile Specific -->
	
	<!-- start: CSS -->
	<link id="bootstrap-style" href="css/bootstrap.min.css" rel="stylesheet">
	<link href="css/bootstrap-responsive.min.css" rel="stylesheet">
	<link id="base-style" href="css/style.css" rel="stylesheet">
	<link id="base-style-responsive" href="css/style-responsive.css" rel="stylesheet">
	<link href="css/table.css" rel="stylesheet">
	
	<!--[if lt IE 7 ]>
	<link id="ie-style" href="css/style-ie.css" rel="stylesheet">
	<![endif]-->
	<!--[if IE 8 ]>
	<link id="ie-style" href="css/style-ie.css" rel="stylesheet">
	<![endif]-->
	<!--[if IE 9 ]>
	<![endif]-->
	
	<!-- end: CSS -->
	

	<!-- The HTML5 shim, for IE6-8 support of HTML5 elements -->
	<!--[if lt IE 9]>
	  <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
	<![endif]-->

	
		
		
</head>
};
}

sub print_RightMenu {
	print qq{<body>
		<div id="overlay">
		<ul>
		  <li class="li1"></li>
		  <li class="li2"></li>
		  <li class="li3"></li>
		  <li class="li4"></li>
		  <li class="li5"></li>
		  <li class="li6"></li>
		</ul>
	</div>	
	<!-- start: Header -->
	<div class="navbar">
		<div class="navbar-inner">
			<div class="container-fluid">
				<a class="btn btn-navbar" data-toggle="collapse" data-target=".top-nav.nav-collapse,.sidebar-nav.nav-collapse">
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
				</a>
				<a class="brand" href="index.html"> <span class="hidden-phone">CancerSeq Project Dashboard</span></a>
								
				
			</div>
		</div>
	</div>
	<!-- start: Header -->
	
		<div class="container-fluid">
		<div class="row-fluid">
				
			<!-- start: Main Menu -->
			<div class="span2 main-menu-span">
				<div class="nav-collapse sidebar-nav">
					<ul class="nav nav-tabs nav-stacked main-menu">
						<li><a href="index.html"><i class="icon-home icon-white"></i><span class="hidden-tablet"> Dashboard</span></a></li>
						
						<li>
							<a class="dropmenu" href="#"><i class="fa-icon-folder-close-alt"></i><span class="hidden-tablet"> CancerSeq </span></a>
							<ul>
								<li><a class="submenu" href="#"><i class="fa-icon-file-alt"></i><span class="hidden-tablet"> GBM_MSSM </span></a></li>
								<li><a class="submenu" href="#"><i class="fa-icon-file-alt"></i><span class="hidden-tablet"> PID4447</span></a></li>
								<li><a class="submenu" href="#"><i class="fa-icon-file-alt"></i><span class="hidden-tablet"> PID4418</span></a></li>
								<li><a class="submenu" href="#"><i class="fa-icon-file-alt"></i><span class="hidden-tablet"> PID4468</span></a></li>
								<li><a class="submenu" href="#"><i class="fa-icon-file-alt"></i><span class="hidden-tablet"> PID4413</span></a></li>
								<li><a class="submenu" href="#"><i class="fa-icon-file-alt"></i><span class="hidden-tablet"> 13006_BreastCancer </span></a></li>
							</ul>	
						</li>
						<li>
							<a class="dropmenu" href="#"><i class="fa-icon-folder-close-alt"></i><span class="hidden-tablet"> Ovarian </span></a>
							<ul>
								<li><a class="submenu" href="#"><i class="fa-icon-file-alt"></i><span class="hidden-tablet"> PT165 </span></a></li>
								<li><a class="submenu" href="#"><i class="fa-icon-file-alt"></i><span class="hidden-tablet"> PT087</span></a></li>
								<li><a class="submenu" href="#"><i class="fa-icon-file-alt"></i><span class="hidden-tablet"> PT218</span></a></li>
							</ul>	
						</li>
					</ul>
				</div><!--/.well -->
				<div class="box">
						<div class="box-header">
							<i class="icon-list"></i><span class="break"></span>Legend
							<div class="box-icon">
								<a href="#" class="btn-minimize"><i class="icon-chevron-up"></i></a>
							</div>
						</div>
						<div class="box-contentSmall">
							<span class=\"label label-success\">&nbsp;</span>  Finished <hr>
							<span class=\"label label-important\">&nbsp;</span>  Not Finished <hr>
							<span class=\"label label-warning\">&nbsp;</span> Initializing <hr>
							<span class=\"label label-defaul\">&nbsp;</span>  Not Applicable <hr>
							WES | Whole exome sequencing <hr>
							WGS | Whole genome sequencing <hr>
							E+G | Exome + Genome combined analysis <hr>
							RNA | PolyA sequencing <hr>
							ES: Curation by Eric Schadt<hr>
							JZ: Curation by Jun Zhu <hr>
							JD: Curation by Joel Dudley
						</div>
				</div>
			</div><!--/span-->
			<!-- end: Main Menu -->
			
			<noscript>
				<div class="alert alert-block span10">
					<h4 class="alert-heading">Warning!</h4>
					<p>You need to have <a href="http://en.wikipedia.org/wiki/JavaScript" target="_blank">JavaScript</a> enabled to use this site.</p>
				</div>
			</noscript>};

}

sub displayStatus {
	my $settings=shift;
	my $sampleName=shift;
	my $processName=shift;
	my $display="";
	my ($rows,$cols)=$flavor{$settings}=~/(\S+)\|(\S+)/;
	my @rows=split(',',$rows);
	my @cols=split(',',$cols);
	my $status="important";
	my $finalCnt=0;
	if($processName=~m/ES|JD|JZ/){
		$display="<span class=\"label label-$status\">&nbsp;</span>\n";
	}elsif($processName=~/Sequencing|FastQ/){
		$display.="<table>";	
			for(my $i=0;$i<@rows;$i++){
				my $flag=0;
				$display.="<tr>";
				if($i == 0){
					## first column
					$display.="<td></td>\n";
					for(my $j=0;$j<@cols;$j++){
						### removing the E+G checks for now
					    #if($cols[$j] eq 'E+G'){$flag++;next;}
						$display.="<td><div class=\"letterP4\">$cols[$j]</div></td>\n";
					}
				}else{
					$display.="<td>$rows[$i]</td>\n";
					my $val=0;
					if($flag > 0){ $val=1;}
					if($projects{$sampleName}{type}=~m/Ovarian/) {$val=0;}
					#else{$val=1;}
					for(my $j=$val;$j<@cols;$j++){
						my $tmpCnt=0;
						($status,$tmpCnt)=getStatus($sampleName,$rows[$i],$cols[$j],$processName);
						$finalCnt+=$tmpCnt;
						$display.="<td><span class=\"label label-$status\">&nbsp;</span></td>\n";
					}
				}
				$display.="</tr>";
			}	
		$display.="</table>";
	}else{
		#$display.="<div class=\"box-content\">\n"
		#		."<table>\n"
		#		."<t>\n"
		#		."<td>\n"
		#		."<table>\n";
		$display="<table>";
		for(my $i=0;$i<@rows;$i++){
			$display.="<tr>";
			if($i == 0){
				## first column
				$display.="<td></td>\n";
				for(my $j=0;$j<@cols;$j++){
					$display.="<td><div class=\"letterP4\">$cols[$j]</div></td>\n";
				}
			}else{
				$display.="<td>$rows[$i]</td>\n";
				for(my $j=0;$j<@cols;$j++){
					my $tmpCnt=0;
					($status,$tmpCnt)=getStatus($sampleName,$rows[$i],$cols[$j],$processName);
					$finalCnt+=$tmpCnt;
					$display.="<td><span class=\"label label-$status\">&nbsp;</span></td>\n";
				}
			}
			$display.="</tr>";
		}
=pod
		$display.="<tr><td>";
		if($processName eq 'BAMs'){
			$display.="<p class=\"btn-group\">
								  <button class=\"btn\">Settings</button>
								  <button class=\"btn\">QC</button>
								  <button class=\"btn\">Status</button>
							</p>";
		}elsif($processName eq 'VCFs'){
			$display.="<p class=\"btn-group\">
								  <button class=\"btn\">View</button>
								  <button class=\"btn\">QC</button>
							</p>";
		}
		$display.="</td></tr>";
=cut
		$display.="</table>";#</td> <td>hardik</td> </tr></table> </div>";
	}

	if($processName=~m/Sequencing|FastQ/){$finalCnt=14;}
	#else{$finalCnt=0;}
	if($projects{$sampleName}{type}=~m/Ovarian/){$finalCnt=0;}
	if($sampleName=~m/13006/){$finalCnt=0;}
	return($display,$finalCnt);
}
sub getStatus {
	my $projectName=shift;
	my $tissueType=shift;
	my $sampleType=shift;
	my $processName=shift;
	my $tag;
	my $cnt=0;
	if($sampleType eq 'WES'){ $tag="exome";}
	elsif($sampleType eq 'WGS'){ $tag="genome";}
	elsif($sampleType eq 'E+G'){ $tag="combined";}
	elsif($sampleType eq 'RNA'){ 
		if($tissueType =~m/Normal|NORMAL|normal/){ return("defaul");}
		else{
			return("success") if($processName=~m/Sequencing|FastQ/ and $tissueType !~m/Normal|NORMAL|normal/);
		}
		#return("warning");
	}
	my $returnVal;
	#if($projectName=~m/13006/){ $returnVal="important";return($returnVal);}
	if($projectName eq 'PID4447') { $projectName="LA";}
	if($projectName eq 'GBM_MSSM') { $projectName="D_751";}
	if($projects{$projectName}{type}=~m/Ovarian/){
		return("warning");
	}else{
		if($processName eq 'Sequencing'){
=pod
		    if($projectName=~m/13006/){
			if($tissueType=~m/Tumor/ and $tag eq 'genome'){ 
			    #print "Got here : $projectName,$tissueType,$sampleType,$processName<br>";
			    return("success",2);
			}else{
			    return("important");
			}
		    }else{
=cut
			return("success");

		    #}
		}elsif($processName eq 'FastQ'){
=put
		    if($projectName=~m/13006/){
			if($tissueType=~m/Tumor/ and $tag eq 'genome'){
			    return("success",2);
			}else{
			    return("important");
			}

		    }else{
=cut
			return("success");

		    #}
		}elsif($processName eq 'BAMs'){
			my $listOfBAMs=`ls -1 $projects{$projectName}{path}/results/*.bam`;
			#my $listOfBAMs=`ls -1 /projects/ngs/research/vaccine/$projectName/*/results/*.bam`;
			chomp($listOfBAMs);
			my @lines=split('\n',$listOfBAMs);
			foreach my $bam (@lines) {
				if($bam=~m/$projectName/){
					if($bam=~m/$tag/){
						my $tmp="$tissueType";
						$tmp=uc($tmp);
						if($bam=~/$tissueType|$tmp/){
							$returnVal="success";
							$cnt+=2;
						}
					}
				}
			}
			
			if($returnVal eq ''){$returnVal="important";return($returnVal,$cnt);}
			else{return($returnVal,$cnt);}
		}elsif($processName eq 'VCFs'){

			my $listOfVCFs=`ls -1 /projects/ngs/research/vaccine/$projectName/*/results/*.vcf`;
			chomp($listOfVCFs);
			my @lines=split('\n',$listOfVCFs);
			my $success=0;
			foreach my $vcf (@lines) {
				if($vcf=~m/$projectName/){
					if($vcf=~m/\/$tag\//){
						##print "$projectName, $tag, $vcf <br>" if($projectName eq 'LA');
						$returnVal="success";
						if($tag eq 'combined'){
							$cnt+=8 if($success==0);
							$success++;
						}else{
							$cnt+=2 if($success==0);
							$success++;	
						}
					}
				}
			}

		if($returnVal eq ''){$returnVal="important";return($returnVal,$cnt);}
		else{return($returnVal,$cnt);}
		}
	}
}

sub print_Pane {
	print qq{			<div id="content" class="span10">
			<!-- start: Content -->
			
			<div>
				<hr>
				<ul class="breadcrumb">
					<li>
						<a href="#">Home</a> <span class="divider">/</span>
					</li>
					<li>
						<a href="#">Dashboard</a>
					</li>
				</ul>
				<hr>
			</div>
					<script src="js/raphael-min.js"></script>
			<div class="row-fluid">
				
				<div class="box">
						<div class="box-header" data-original-title>
							<h2><i class="icon-user"></i><span class="break"></span>Dashboard</h2>
							<div class="box-icon">
								<!-- <a href="#" class="btn-setting"><i class="icon-wrench"></i></a> -->
								<a href="#" class="btn-minimize"><i class="icon-chevron-up"></i></a>
								<!-- <a href="#" class="btn-close"><i class="icon-remove"></i></a> -->
							</div>
						</div>
						<div class="box-content">
							<table class="table bootstrap-datatable datatable">
							<!-- <table class="table"> -->
							  <thead>
								  <tr>
									  <th>Project</th>
									  <th>Sequencing</th>
									  <th>FastQ</th>
									  <th>BAMs</th>
									  <th>VCFs/Expression</th>
									  <th>Metrics</th>
                                                                          <th>ES</th>
                                                                          <th>JZ</th>
                                                                          <th>JD</th>
								  </tr>
							  </thead>   
							  <tbody>};

	my @groups;
	#print qq{};
	my %unique;
	while(my ($samples,$details)=each(%projects)) {
		my $fullRow="";
		my ($sampleName,$settings);
		my $fullAPI_path;
		$sampleName="$samples";
		if($unique{$samples} > 0) {next;}
		else{$unique{$samples}++;}
		while(my ($key,$value)=each(%{$details})){
			#$fullRow.="$key ---> $value<br>";
			$fullAPI_path="$value" if($key eq 'path');
			if($value=~m/,/){
				($settings)=$value=~/(\S+),\S+/;
			}else{
				$settings="$value";

			}
		}

		my $statusRow="";
		my $progressCount=10;

		my $printStuff;
		my $cnt=0;
		#my $currStatus=`curl -k https://shahh06.u.hpc.mssm.edu/dashboard/markm/forms/jsonmaker.cgi?path=/projects/ngs/research/cancer/PID4596/combined`;
		#$fullRow.="STAUTSAFADFAFADF is $currStatus";
		my $json_text=`./markm/forms/jsonmaker.cgi $fullAPI_path`;
		#my $json_text=`./markm/forms/jsonmaker.cgi /projects/ngs/research/cancer/PID4596/combined/`;
		#$fullRow.="$json_text";
		my $json = JSON->new;
		my $data = $json->decode($json_text);
		#$myUtil->prettyPrint($data);
		#for ( @{$data->{data}} ) {
		 #  $fullRow.="$_->{name}\n";
		#}
		($printStuff,$cnt)=displayStatus($settings,$sampleName,"Sequencing");
		$progressCount+=$cnt;
		$fullRow.="<td>$printStuff</td>";
		($printStuff,$cnt)=displayStatus($settings,$sampleName,"FastQ");
		$progressCount+=$cnt;
		$fullRow.="<td>$printStuff</td>";
		($printStuff,$cnt)=displayStatus($settings,$sampleName,"BAMs");
		$progressCount+=$cnt;
		my $hardikBAMs;
		$hardikBAMs.=qq{
		<div class="btn-group">
							<button class="btn btn-small">BAM Files</button>
							<button class="btn btn-small dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>
							<ul class="dropdown-menu">
                                                        <li class="divider"></li>
								<li><a href="#"><i class="icon-tint"></i>Coverage Tools</a></li>
};
							while(my ($key,$value)=each(%{$data})){
								if($key=~m/SAMPLE/){
									foreach my $bam (@{$value}){
										$hardikBAMs.="<li style='font-size:8'><a href=\"#\"><i class=\"icon-tag\"></i>$bam</a></li>";
									}
								}
							}
							$hardikBAMs.=qq{								</ul>
						</div>};

		$fullRow.= "<td>$printStuff $hardikBAMs</td>";

		($printStuff,$cnt)=displayStatus($settings,$sampleName,"VCFs");
		$progressCount+=$cnt;
		my $hardikVCFS;

		$hardikVCFS.=qq{
		<div class="btn-group">
							<button class="btn btn-small">VCF Files</button>
							<button class="btn btn-small dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>
							<ul class="dropdown-menu">
                                                                <li class="divider"></li>
								<li><a href="#"><i class="icon-tint"></i> Separated link</a></li>};

							while(my ($key,$value)=each(%{$data})){
								if($key eq 'vcfset'){
									foreach my $vcf (@{$value}){
										$hardikVCFS.="<li style='font-size:8'><a href=\"#\"><i class=\"icon-tag\"></i>$vcf</a></li>";
									}
								}
							}
							$hardikVCFS.=qq{								</ul>
						</div>};

		$fullRow.="<td>$printStuff $hardikVCFS</td>";		

                ###### Mark's additions!
                my $markButton;
                $markButton.=qq{
		<div class="btn-group">
							<button class="btn btn-small">Metrics</button>
							<button class="btn btn-small dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>
							<ul class="dropdown-menu">
                                                        <li class="divider"></li>
                                <li><a href="#"><i class="icon-tint"></i> Separated link</a></li>};
                
							while(my ($key,$value)=each(%{$data})){
								if($key eq 'metricset'){
									foreach my $metric (@{$value}){
                                                                            $markButton.="<li style='font-size:8'><a href=\"#\"><i class=\"icon-tag\"></i>$metric</a></li>";
                                                                        }
                                                                }
                                                        }
                $markButton.=qq{	
				</ul>
                                </div>};
                $fullRow.="<td>$markButton</td>";
                ###### </Mark's additions!>

		($printStuff,$cnt)=displayStatus($settings,$sampleName,"ES");
		$progressCount+=$cnt;
		$fullRow.="<td>$printStuff </td>";		
		($printStuff,$cnt)=displayStatus($settings,$sampleName,"JZ");
		$progressCount+=$cnt;
		$fullRow.="<td>$printStuff</td>";		
		($printStuff,$cnt)=displayStatus($settings,$sampleName,"JD");
		$progressCount+=$cnt;
		$fullRow.="<td>$printStuff</td>";		

		#print "<td><table>$display</table></td>";
		#print "<td><table>$display</table></td>";
		#print "<td><table>$display</table></td>";
		#print "<td><table>$display</table></td>";
		#$status=getStatus($sampleName,"NA","other");
		#$status="warning";
		#print "<td><span class=\"label label-$status\">&nbsp;</span></td>";
		#print "<td><span class=\"label label-$status\">&nbsp;</span></td>";
		#print "<td><span class=\"label label-$status\">&nbsp;</span></td>";

		$statusRow.="<tr><td>$sampleName";
		my ($color,$direction,$secondColor);
		if($progressCount > 50){
		    $color="green";$direction="up";
		    $secondColor="green";
		}else{
		    $color="red";$direction="down";
		    $secondColor="orange";
		}
		$statusRow.=qq{ <!-- <div class="span2" onTablet="span4" onDesktop="span2"> -->
                    	<div class="circleStatsItem $color">
							<i class="fa-icon-thumbs-$direction"></i>
							<span class="plus">+</span>
							<span class="percent">%</span>};
		$statusRow.="<input type=\"text\" value=\"$progressCount\" class=\"$secondColor"."Circle\" />";
		$statusRow.=qq{</div>
						<!-- <div class="box-small-title"></div> -->
					<!-- </div> -->};
		$statusRow.="</td>";

		print "$statusRow $fullRow</tr>";
	}


	print qq{  </tbody>
							</table>
						</div>	
				</div>	
				<!--	##### the LEGEND goes here -->
			</div>
			
			<!-- end: Content -->
			</div><!--/#content.span10-->
			</div><!--/fluid-row-->
				
				
		<div class="modal hide fade" id="myModal">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal">×</button>
				<h3>Settings</h3>
			</div>
			<div class="modal-body">
				<p>Here settings can be configured...</p>
			</div>
			<div class="modal-footer">
				<a href="#" class="btn" data-dismiss="modal">Close</a>
				<a href="#" class="btn btn-primary">Save changes</a>
			</div>
		</div>
		
		<div class="clearfix"></div>
		
		<footer>
			<p>
				<span style="text-align:left;float:left">&copy; <a href="#" target="_blank">HardikShah</a> 2013</span>
			
			</p>

		</footer>
				
	</div><!--/.fluid-container-->

	<!-- start: JavaScript-->

		<script src="js/jquery-1.9.1.min.js"></script>

	<script src="js/jquery-migrate-1.0.0.min.js"></script>
	
		<script src="js/jquery-ui-1.10.0.custom.min.js"></script>
	
		<script src="js/jquery.ui.touch-punch.js"></script>
	
		<script src="js/bootstrap.min.js"></script>
	
		<script src="js/jquery.cookie.js"></script>
	
		<script src='js/fullcalendar.min.js'></script>
	
		<script src='js/jquery.dataTables.min.js'></script>

		<script src="js/excanvas.js"></script>
	<script src="js/jquery.flot.min.js"></script>
	<script src="js/jquery.flot.pie.min.js"></script>
	<script src="js/jquery.flot.stack.js"></script>
	<script src="js/jquery.flot.resize.min.js"></script>
<script src="js/jquery.chosen.min.js"></script>
	
		<script src="js/jquery.uniform.min.js"></script>
		
		<script src="js/jquery.cleditor.min.js"></script>
	
		<script src="js/jquery.noty.js"></script>
	
		<script src="js/jquery.elfinder.min.js"></script>
	
		<script src="js/jquery.raty.min.js"></script>
	
		<script src="js/jquery.iphone.toggle.js"></script>
	
		<script src="js/jquery.uploadify-3.1.min.js"></script>
	
		<script src="js/jquery.gritter.min.js"></script>
	
		<script src="js/jquery.imagesloaded.js"></script>
	
		<script src="js/jquery.masonry.min.js"></script>
	
		<script src="js/jquery.knob.js"></script>
	
		<script src="js/jquery.sparkline.min.js"></script>

		<script src="js/custom.js"></script>
		
	
</body>
</html>
};
}
