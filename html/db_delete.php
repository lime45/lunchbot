<?php
$db = new SQLite3('/home/ddedrick/innovation.db');
if(($_GET["table"] != "messages") && ($_GET["table"] != "sqlite_sequence"))
{
   $results = $db->exec("DELETE FROM " . $_GET["table"] . " where something='" SQLite3::escapeString($_GET["value"]) . "';");
}
?>
