<?php 
class OxGdImage {
	
	public $image;
	public $colors; 
	function __construct($x = null, $y=null){
		if($x != null && $y != null){
			$this->create($x,$y);
			//$this->allocate();
		}
	}
	function create($x, $y){
		$this->image = imagecreatetruecolor($x, $y);	
	}
//	function allocate(){		
//		$this->colors['white'] = $this->colorAllocate(255, 255, 255);
//		$this->colors['black'] = $this->colorAllocate(0, 0, 0);
//		$this->colors['grey'] = $this->colorAllocate(128, 128, 128);
//		$this->colors['red'] = $this->colorAllocate(255, 0, 0);
//		$this->colors['blue'] = $this->colorAllocate(10, 10, 255);
//	}
	function colorAllocate($r, $g, $b){
		return imagecolorallocate($this->image, $r, $g, $b);
	}
	function fill($color){
		imagefill($this->image, 0, 0, $color);
	}
	function imageText($font, $size, $text, $x, $y, $rgbs, $angle = 0){
		$m = sizeof($rgbs)-1;
		foreach($rgbs as $rgb){
			$c1 = $this->colorAllocate($rgb[0], $rgb[1], $rgb[2]);
			imagettftext($this->image, $size, $angle, $x+$m, $y+$m, $c1, $font, $text);		
			$m = $m-1; 
		}	
	}
	
	function imagePng($file = null){
		imagepng($this->image, $file);
		//imagedestroy($this->image);
	}	
	function sizeFromBbox($bbox){
		$x = $bbox[2]-$bbox[0];
		$y = $bbox[1]-$bbox[5];
		return array($x, $y);
	}
}


class OxGdImageText extends OxGdImage {
	function __construct($font, $size, $text, $where='C:\gdimage.png', $angle = 0){
		$bbox = imagettfbbox($size, $angle, $font, $text);
		$xy = $this->sizeFromBbox($bbox);
		
		$c1 = array(200,200,200);
		$c2 = array(160,160,160);
		$c3 = array(230,230,230);
		$c4 = array(240,240,240);
		$c5 = array(250,250,250);
		
		//$c2 = array(0, 0, 0);
		$rgbs = array($c5, $c4, $c3, $c2, $c1);	
		//$rgbs = array($c2);
		$es = sizeof($rgbs)-1;
		
		OxGdImage::__construct($xy[0]+40+$es, $xy[1]+40+$es);
		$this->fill($this->colorAllocate(255, 255, 255));
		
		$this->imageText($font, $size, $text, 0, -1*$bbox[5]+10, $rgbs);
		$this->imagePng($where);
	}
}
?> 

