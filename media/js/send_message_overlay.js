(function( $ ){
  $.fn.send_message_overlay = function(options) {
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

    var loaded_code = '';

    var rand = Math.floor(Math.random()*10000);
    $.ajax({ async: false,  
             url: "/static/html/send_message_overlay.html?i="+rand+" #top_level", 
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

    function build_send_message_overlay(div) {

      var to_parent = div.find("#to_parent"); 

      div.find(".close_send_message_overlay").click(function(e) {
        e.preventDefault();       
        div.fadeOut();
      });

      div.find("#send_message").click(function(e) {
        e.preventDefault();
        var subject = $("#subject").val();
        var message = $("#message").val();
        var to_user_id = $("#to_user_id").val();

        var response = send_message(to_user_id, subject, message);
        div.fadeOut();
        div.remove();

        var rso = load_remote("#message_sent_overlay");
        $("body").append(rso);
        rso.fadeIn();
        setTimeout(function() { rso.fadeOut(); }, 1000);

      });

      return div;      
    }
    var ds = {
      'name':settings["name"],
      'to_user_id':settings["to_user_id"],
    };
    
    var div = load_remote_tmpl('#send_message_overlay_wrapper', ds);

    var q = build_send_message_overlay(div);

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
