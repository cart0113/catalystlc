<?php
class OxFile {
	public static function getDirs($rootSearchDir, &$dirs){
		if ($handle = opendir($rootSearchDir)) {
			while (false !== ($file = readdir($handle))) {
				if ($file != "." && $file != "..") {
					$fileName = $rootSearchDir . "/" . $file;
					if(is_dir($fileName)){
						$dirs[] = $fileName;
						$newDirs[] = $fileName;
					}
				}
			}
			if($newDirs){
				foreach($newDirs as $newDir){
					OxFile::getDirs($newDir, &$dirs);
				}
			}
		}
	}
	public static function getFiles($rootSearchDir, $fileExt, $addDir=false, $recursive = true) {
		if(is_array($rootSearchDir)){
			$fileArray = array();
			foreach($rootSearchDir as $aRootSearchDir){
				$fileArray += OxFile::getFiles($aRootSearchDir, $fileExt, $addDir);
			}
		}
		else {
			if(is_array($fileExt)){
				$fileArray = array();
				foreach($fileExt as $aFileExt){
					$fileArray += OxFile::getFiles($rootSearchDir, $aFileExt, $addDir);
				}
			}
			else{
				$fileArray = array();
				$n = strlen($fileExt);
				if ($handle = opendir($rootSearchDir)) {
					while (false !== ($file = readdir($handle))) {
						//print $file . "<br/>";
						if ($file != "." && $file != "..") {
							$fileName = $rootSearchDir . "/" . $file;
							if(strtoupper(substr($file, strlen($file)-$n)) == strtoupper($fileExt)){
								$name = substr($file, 0, strlen($file)-$n);
								//print "<br>$name";
								//$fileName = str_replace("/x", "//x", $fileName);
								if($addDir == true){
									$names = explode("/", $fileName);
									$name = array_pop($names);
									$name = array_pop($names) .  "." . $name;
								}
								//$name = strtolower($name);
								$fileArray[$name] = $fileName;
							}
							if(is_dir($fileName) && $recursive){
								$fileArray += OxFile::getFiles($fileName, $fileExt, $addDir);
							}
						}
					}
					closedir($handle);
				}
			}
		}
		return $fileArray;
	}

	/**
	* Create a new directory, and the whole path.
	*
	* If  the  parent  directory  does  not exists, we will create it,
	* etc.
	*
	* @param string the directory to create
	* @param int the mode to apply on the directory
	* @return bool return true on success, false else
	*/
	function mkdirs($dir, $mode = FS_RIGHTS_D) {
		$stack = array(basename($dir));
		$path = null;
		while ( ($d = dirname($dir) ) ) {
			if ( !is_dir($d) ) {
				$stack[] = basename($d);
				$dir = $d;
			} else {
				$path = $d;
				break;
			}
		}
		if ( ( $path = realpath($path) ) === false )
		return false;

		$created = array();
		for ( $n = count($stack) - 1; $n >= 0; $n-- ) {
			$s = $path . '/'. $stack[$n];
			if ( !mkdir($s, $mode) ) {
				for ( $m = count($created) - 1; $m >= 0; $m-- )
				rmdir($created[$m]);
				return false;
			}
			$created[] = $s;
			$path = $s;
		}
		return true;
	}
}


?>