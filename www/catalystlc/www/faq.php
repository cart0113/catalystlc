<?php
	session_start(); 
	require_once("LcPageMaker.php");
	$pageMaker = new LcPageMaker("faq"); 
	$pageMaker->doIt();
?>