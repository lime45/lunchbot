<html>
   <head>
      <script language="javascript">
         function change_selection()
         {
            var xmlhttp = new XMLHttpRequest();
            var selection = document.getElementById("table_selection");
            var div = document.getElementById("content_div");
            xmlhttp.open("GET","http://farscape.dhcp.crus.lexmark.com/~ddedrick/db_select.php?table=" +  selection.value,false);
            xmlhttp.send();
            var items = JSON.parse(xmlhttp.responseText);
            item_str = "<table border=\"1\">";
            for ( var i=0; i < items.length; i++)
            {
               item_str += "<tr><td>" + items[i] + "</td></tr>";
            }
            item_str += "</table>";
            div.innerHTML = item_str;

         }
         window.onload = change_selection;
      </script>
   </head>
   <body id="main_body">
      <form action="db_insert.php">
      <?php
      
      $db = new SQLite3('/home/ddedrick/innovation.db');
      $results = $db->query("SELECT * FROM sqlite_master WHERE type='table';");
      if($results)
      {
         echo "Select Table:<select name=\"table\" id=\"table_selection\" onchange=\"change_selection()\">";
         $data = array();
         while ($row = $results->fetchArray())
         {
            if(($row["name"] != "sqlite_sequence") && ($row["name"] != "messages"))
 
            {

               echo "<option value=\"" . $row["name"] . "\">" . $row["name"] . "</option>";
            }
         }
         echo "</select>";
      }
      else
      {
         echo "fail";
      }
      
      ?>
      <input type="text" name="value">
      <input type="submit" value="Add">
      </form>
      <div id="content_div">
      </div>
   </body>
</html>
