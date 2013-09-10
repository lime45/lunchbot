<?php
$db = new SQLite3('/home/ddedrick/innovation.db');
$results = $db->query("SELECT * FROM " . $_GET["table"]);
if($results)
{
   $data = array();
   while ($row = $results->fetchArray())
   {
      array_push($data,$row[1]);
   }
   echo json_encode($data);
}
else
{
   echo("fail");
}



?>
