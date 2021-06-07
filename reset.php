<?php

if (file_exists('white')) {
	unlink('white');
}

if (file_exists('black')) {
	unlink('black');
}

if (file_exists('whitenotmovedyet')) {
	unlink('whitenotmovedyet');
}

if (file_exists('blacknotmovedyet')) {
	unlink('blacknotmovedyet');
}

?>