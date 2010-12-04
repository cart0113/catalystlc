<?php
	session_start();
	$pdf = $_GET['pdf'];
	if($_GET['type'] != null){
		$pdf = $pdf . "&type=" . $_GET['type']; 
	}
	if($_SESSION['lc_pdfon'] || $pdf == null){
		header("Location: " . $_SESSION['lc_lastpage']);
		exit(); 
	}
	$_SESSION['lc_pdfon'] = true;
	if($_SERVER['SERVER_NAME'] == "www.catalystlc.org"){
		$pdf = "http://disk.catalystlc.org/public/clc/" . $pdf; 
	}
	header("location: $pdf");
?>
<!--
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<meta http-equiv="Refresh" content="2; URL=<?php print $pdf;?>">
<head>
<title>Catalyst Learning Center
</title>
</head>
<body>
	<div style="text-align:center;">
	<div style="text-align: center; padding-top: 200px;">
			<img src="wait.gif"/>
			<div style="padding-top: 50px; font-size: 9pt;font-family: Verdana, sans-serif; font-style: italic; color: #666666;">
				-- please wait while pdf loads -- 
			</div>
	</div>
	</div>
</body>
</html>
-->