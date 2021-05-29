<?php

ini_set('display_errors', '1');
ini_set('display_startup_errors', '1');
error_reporting(E_ALL);

// Assign sides randomly using empty files to track assignments
if (isset($_GET['newGame'])) {
	if (!file_exists('black') && !file_exists('white') && !file_exists('whitenotmovedyet') && !file_exists('blacknotmovedyet')) {
		touch('black');
		touch('white');
		if (round(rand(0, 1))) {
			unlink('white');
			touch('whitenotmovedyet');
			echo 'white';
		}
		else {
			unlink('black');
			touch('blacknotmovedyet');
			echo 'black';
		}
	}
	elseif (file_exists('black') && !file_exists('white')) {
		unlink('black');
		touch('blacknotmovedyet');
		echo 'black';
	}
	elseif (!file_exists('black') && file_exists('white')) {
		unlink('white');
		touch('whitenotmovedyet');
		echo 'white';
	}
	else {
		throw Exception('Both white and black files present on server');
	}
}
elseif (isset($_GET['readyToStart'])) {
    if (file_exists('white') || file_exists('black')) {
        echo 'WAIT';
    }
    else {
        echo 'GO';
    }
}
// Decide whether to transmit or receive based on what information was passed
else {
	if (isset($_GET['id'])) {
		$id = $_GET['id'];
		sendMove((int)$id);
	}
	elseif (isset($_GET['player']) and isset($_GET['row1']) and isset($_GET['col1']) and isset($_GET['row2']) and isset($_GET['col2'])) {
		$player = (int)$_GET['player'];
		$row1 = (int)$_GET['row1'];
		$col1 = (int)$_GET['col1'];
		$row2 = (int)$_GET['row2'];
		$col2 = (int)$_GET['col2'];
		receiveMove($player, $row1, $col1, $row2, $col2);
	}
	else {
		throw new Exception('Not passed in expected data');
	}
}

// Create PDO object for database connection
function connect() {
	$host = 'localhost';
	$db   = 'chess';
	$user = 'chessplayer';
	$pass = 'time4chess!';
	$charset = 'utf8mb4';

	$dsn = "mysql:host=$host;dbname=$db;charset=$charset";
	$options = [
		PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
		PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
		PDO::ATTR_EMULATE_PREPARES   => false,
	];
	try {
		 $pdo = new PDO($dsn, $user, $pass, $options);
	} catch (\PDOException $e) {
		 throw new \PDOException($e->getMessage(), (int)$e->getCode());
	}
	return $pdo;
}

// Determine highest ID in database (should represent previous entry)
function highestId($pdo) {
	$sql = "select max(id) as maxId from chess.moves;";
	$stmt = $pdo->prepare($sql);
	$stmt->execute();
	$row = $stmt->fetch(PDO::FETCH_ASSOC);
	return (int)$row['maxId'];
}

// Receive a move from a remote player to store in the database
function receiveMove(int $player, int $row1, int $col1, int $row2, int $col2) {

	$pdo = connect();
	$sql = "insert into chess.moves (player, row1, col1, row2, col2) values (:player, :row1, :col1, :row2, :col2);";
	$stmt = $pdo->prepare($sql);
	$stmt->bindValue(':player', $player);
	$stmt->bindValue(':row1', $row1);
	$stmt->bindValue(':col1', $col1);
	$stmt->bindValue(':row2', $row2);
	$stmt->bindValue(':col2', $col2);
	if ($stmt->execute()) {
	    if (($player == 1) && file_exists('whitenotmovedyet')) {
	        unlink('whitenotmovedyet');
	    }
	    if (($player == 2) && file_exists('blacknotmovedyet')) {
	        unlink('blacknotmovedyet');
	    }
		echo $pdo->lastInsertId('id');
		return true;
	}
	else {
		return false;
	}
}

// Transmit [the most recent] move in the database [from opposing side]
function sendMove(int $id) {
	$pdo = connect();
	$maxId = highestId($pdo);
	if ((($maxId > $id) && ($id > 0)) || (($id == 0) && !file_exists('whitenotmovedyet'))) {
		$sql = "select player, row1, col1, row2, col2 from chess.moves where id=:maxId;";
		$stmt = $pdo->prepare($sql);
		$stmt->bindValue(':maxId', $maxId);
		$stmt->execute();
		$row = $stmt->fetch(PDO::FETCH_ASSOC);
		echo $row['player'];
		echo $row['row1'];
		echo $row['col1'];
		echo $row['row2'];
		echo $row['col2'];
		return true;
	}
	elseif (($maxId == $id) || (($id == 0) && (file_exists('whitenotmovedyet')))) {
		echo 'WAIT';
		return true;
	}
	else {
		throw new Exception('Move synchronization error');
		return false;
	}
}

?>
