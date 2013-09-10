<html>
   <head>
      <script language="javascript">
         var xmlhttp;
         var map_obj;
         <?php
            if($_GET["channel"])
            {
               echo "var channel = \"" . $_GET["channel"] . "\";\n";
            }
            else
            {
               echo "var channel = \"innovationcouch\";\n";
            }
         ?>
         function convert_x(x,width, divisor)
         {
            var int_x = parseInt(x);
            int_x+= Math.floor(divisor/2);
            int_x*=width;
            int_x/=divisor;
            return int_x;
         }
         function convert_y(y,height, divisor)
         {
            var int_y = parseInt(y);
            int_y+= Math.floor(divisor/2);
            int_y = divisor - 1 - int_y;
            int_y*= height;
            int_y/=divisor;
            return int_y;
         }
         function update_map()
         {
            if (xmlhttp.readyState==4 && xmlhttp.status==200)
            {
               map_obj = JSON.parse(xmlhttp.responseText);
               var rooms = map_obj.rooms;
               var canvas = document.getElementById("main_canvas");
               var context = canvas.getContext("2d");
               var body = document.getElementById("main_body");
               canvas.width = body.clientWidth-1;
               canvas.height = body.clientHeight-1;
               var height = canvas.height/map_obj.height;
               var width = canvas.width/map_obj.width;

               for (var i=0; i<rooms.length;i++)
               {
                  var x = convert_x(rooms[i].x,canvas.width, map_obj.width);
                  var y = convert_y(rooms[i].y,canvas.height, map_obj.height);

                  context.strokeRect(x,y,width,height);
                  context.font = "10pt Calibiri";
                  context.fillText(rooms[i].name,x,y+14);
               }
            }
         }
         function mouse_over(event)
         {
            if(map_obj)
            {
               var canvas = document.getElementById("top_canvas");
               var height = canvas.height/map_obj.height;
               var width = canvas.width/map_obj.width;
               var context = canvas.getContext("2d");
               context.clearRect(0,0,canvas.width,canvas.height);
               rooms = map_obj.rooms;
               for( var i=0;i<rooms.length;i++)
               {
                  var x = convert_x(rooms[i].x,canvas.width,map_obj.width);
                  var y = convert_y(rooms[i].y,canvas.height,map_obj.height);
                  if((event.x > x) && (event.x < x+width))
                  {
                     if((event.y > y) && (event.y < y+height))
                     {
                        var str = new Array();
                        str.push("Players:");
                        for(var j=0;j<rooms[i].people.length;j++)
                        {
                           str.push(rooms[i].people[j]);
                        }
                        str.push("Items:");
                        for(var j=0;j<rooms[i].objects.length;j++)
                        {
                           str.push(rooms[i].objects[j]);
                        }
                        max_len=0;
                        total_height = 0;
                        for(var j=0; j <str.length;j++)
                        {
                           var measure = context.measureText(str[j]);
                           if(measure.width > max_len)
                           {
                              max_len = measure.width;
                           }
                           total_height += 14;
                        }
                        context.fillStyle = "#F3F781";
                        context.fillRect(event.x, event.y, max_len,total_height + 5);
                        context.fillStyle = "#000000";
                        for(var j = 0; j < str.length;j++)
                        {
                           context.fillText(str[j],event.x, event.y + 14*(j+1));
                        }
                     }
                  }
               }
            }
         }
         window.onload = function()
         {
            var canvas = document.getElementById("top_canvas");
            var body = document.getElementById("main_body");
            canvas.width = body.clientWidth-1;
            canvas.height = body.clientHeight-1;
            xmlhttp = new XMLHttpRequest();
            xmlhttp.onreadystatechange = update_map;
            xmlhttp.open("GET","lunch_map.php?channel=" + channel,true);
            xmlhttp.send();

            body.onmousemove = mouse_over;
         }

      </script>
   </head>
   <body id="main_body">
      <canvas id="top_canvas" style="position:absolute;top:0;left:0;z-index:2;">
      </canvas>
      <canvas id="main_canvas" style="position:absolute;top:0;left:0;z-index:1;">
      </canvas>
   </body>
</html>
