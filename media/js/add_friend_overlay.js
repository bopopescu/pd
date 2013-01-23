(function( $ ){
  $.fn.add_friend_overlay = function(options) {
    var settings = {
      // 'something':'something',
      // 'par': [{'fuck':"1"},{'fuck':"2"},{'fuck':"3"}],
      // 'parents': [{'id':'1','name':'Yolanda Jackson'},{'id':'2','name':'Marcus Jackson'}],
      // 'children': [ {'id':'4', 'name':'Timmy'}, { 'id':'5', 'name':'Melinda'}],
      // 'child_id': 8,
    };

    if ( options ) { 
      $.extend( settings, options );
    }

    var callback = false;
    if (settings["callback"]) {
      callback = settings["callback"]; 
    } 
    var element = false;
    if (settings["element"]) {
      element = settings["element"];
    }

    var known_from_child = 0;
    
    if (settings["from_child"]) {
      known_from_child = settings["from_child"];
    }
    var loaded_code = '';

    var rand = Math.floor(Math.random()*10000);
    
    $.ajax({ async: false,  
             url: "/static/html/add_friend_overlay.html?i="+rand+" #top_level", 
             success:function(data) { loaded_code = $(data); },
         });
           
    function load_remote(selector, callback) {
      return loaded_code.find(selector)
    }

    function load_remote_tmpl(selector, ds, callback) {
      var temp_tmpl = load_remote(selector, callback);
      var temp = $.tmpl(temp_tmpl, ds);
      return temp;
    }

    function build_add_friend_overlay(div) {

      var to_parent = div.find("#to_parent"); 
      for (prnt_idx in settings["parents"]) {
        var parent = settings["parents"][prnt_idx];
        to_parent.append($("<option value=\""+parent["id"]+"\">"+ parent["name"] +"'s</option>"));
      }

      var from_child = div.find("#from_child"); 
      for (chld_idx in settings["children"]) {
        var child = settings["children"][chld_idx];
        var selected = '';
        if (child["id"] == known_from_child) {
          selected = 'selected="selected"';
        }
        from_child.append($("<option value=\""+child["id"]+"\""+ selected + ">"+ child["name"] +"'s</option>"));
      };


      function cancel(e) {
        e.preventDefault();       
        var response = false;
        div.fadeOut();
        div.remove();
        if (callback) { callback(response, element); }
      }

      div.find("#close_overlay").click(cancel);      
      div.find("#cancel").click(cancel);


      div.find("#add_friend_form").submit(function(e) {
        e.preventDefault();
        var to_child = $("#to_child").val();
        var to_user = $("#to_parent :selected").val();
        var from_child = $("#from_child :selected").val();
        var how_related = $("input[name=how]:checked").val();
        var message = $("#how_text").val();
        if ((how_related == '5') && (! message.length)) {
            $('#afo_error_span').html('Please explain how your kids know each other');
        } else {

          var ds = {
            "to_user": to_user,
            "to_child": to_child,
            "from_child": from_child,
            "message": message,
            "how_related": how_related,
            "source": "add_friend_overlay",
          }

          var response = send_invite(ds);

          div.fadeOut();
          div.remove();
          var success = false;
          if (response["success"]) {
              success = true;
              var rso = load_remote("#request_sent_overlay");
              $("body").append(rso);
              rso.fadeIn();
              setTimeout(function() { rso.fadeOut(); }, 1000);
          }
  
          if (callback) { callback(success, element); }
        }
      });

      return div;      
    }
    var ds = {
      'child_id':settings["child_id"],
      'child_age':settings["child_age"],
    };
    
    var div = load_remote_tmpl('#add_friend_overlay_wrapper', ds);
    var q = build_add_friend_overlay(div);

    q.hide();
    $("body").append(q);

    var lw = q.find(".lightbox_wrapper");
    lw.css('top',$(window).scrollTop() + 100);

    var maybe_new_height = $(window).scrollTop() + 100 + lw.outerHeight();

    var set_height = $(document).height();
    if (maybe_new_height > set_height) {
      set_height = maybe_new_height;
    }   

    q.height(set_height);

    q.fadeIn();

  };
})( jQuery );
