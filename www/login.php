<?php 
	session_start(); 
	
	$_SESSION['lc_username'] = $_POST['username'];
	$_SESSION['lc_password'] = $_POST['password'];
	
	if($_SERVER['SERVER_NAME'] == 'www.clc.org'){
		header("Location: http://tutor.clc.org/home/index.php?ox_action=login&username=" . $_SESSION['lc_username'] . "&password=". $_SESSION['lc_password']);
	}
	else {
		header("Location: http://tutor.catalystlc.org/home/index.php?ox_action=login&username=" . $_SESSION['lc_username'] . "&password=". $_SESSION['lc_password']);
	}
	
	exit();
		
	$send = false; 
			
	$tutorName = "Guest Tutor";
	$studentName = "Rocio";
	$level = "guest";
	
	if($username=="cart0113" && $password == "f1ingerm3huty"){
		$send = true; 
		setcookie("username", "cart0113");
		$tutorName = "Andrew Carter";
		$studentName = "Rocio";
		$level = "superuser";
	}
	if($username=="guest" && $password == "guest"){
		$send = true; 
		$tutorName = "Guest Visitor";
		$studentName = "Rocio";
		$level = "guest";
	}
	if($username=="jill" && $password="jill"){
		$send=true; 
		$tutorName = "Jill Gjevre";
		$studentName = "Rocio";
		$level = "tutor";
	}
	if($username=="erika" && $password == "erika"){
		$send = true;
		header("Location: http://tutor.catalystlc.org/");
		exit();
		$tutorName = "Erika Sass";
		$studentName = "Kadie"; 
		$level = "tutor";
	}	
	
	if($username=="abby" && $password == "abby"){
		$send = true; 
		$tutorName = "Abby Roza";
		$studentName = "Amina";
		$level = "tutor";
	}	
	
	if($send){
		
		if($username != 'cart0113' && $ip != '192.168.0.100'){
			
			$ip = $_SERVER['REMOTE_ADDR'];
			$file = fopen("login.xlcml", "a+");
			$date = date('l dS \of F Y h:i:s A');
			fwrite($file, "<tr><td style='padding-right: 25px; padding-top: 5px;'>User: $username</td><td style='padding-right: 25px; padding-top: 5px;'>IP: $ip</td><td style='padding-top: 5px;'>Date: $date</td></tr>\n");
			fclose($file); 
		}
		
		$_SESSION['lcusername'] = $username;
		$_SESSION['tutor_name'] = $tutorName;
		$_SESSION['sn_first'] = $studentName;
		$_SESSION['level'] = $level ;	
		
		header("Location: " . $_SESSION['lc_url'] . "/welcome/welcome.php");
		
	}
	else{
		header("Location: ./index.php");
	}
		
?>