<?php
if($_GET["channel"])
{
   $channel = "#" . $_GET["channel"];
}
else
   $channel = "#innovationcouch";

$socket = stream_socket_client('unix:///tmp/' . $channel,$errno,$errstr);
if ($socket)
{
   fwrite($socket, "locations");
   $str = "";
   while($str .= fread($socket,4096))
   {
      if(substr_count($str,"{") == substr_count($str,"}"))
         break;
   }
   echo $str;
   fclose($socket);
}
?>
