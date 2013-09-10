<?php
$db = new SQLite3('/home/ddedrick/innovation.db');
if(($_GET["table"] != "messages") && ($_GET["table"] != "sqlite_sequence"))
{
   $results = $db->exec("INSERT INTO " . $_GET["table"] . " values " . "((select MAX(id) from " . $_GET["table"] . ") + 1,'" . SQLite3::escapeString($_GET["value"]) . "');");
   if(!$results)
   {
      echo "try again";
      echo("INSERT INTO " . $_GET["table"] . " values " . "((select MAX(id) from " . $_GET["table"] . ") + 1,'" . SQLite3::escapeString($_GET["value"]) . "','0');");
      $results = $db->exec("INSERT INTO " . $_GET["table"] . " values " . "((select MAX(id) from " . $_GET["table"] . ") + 1,'" . SQLite3::escapeString($_GET["value"]) . "','0');");

   }
}
?>
