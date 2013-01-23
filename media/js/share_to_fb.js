var got_fb_perms = false;
var got_fb = false;
var ds = { };

ajax_async_call('/profiles/get_fb_status/', ds, function(data) {
  got_fb = data["got_fb"];
  got_fb_perms = data["got_fb_perms"];
});


(function( $ ){
  $.fn.share_to_fb = function(options) {

    var settings = {
      'loading_function':function(done) { if (done) { $("#loading").hide(); } else { $("#loading").show();  }  },
    };

    if ( options ) { 
      $.extend( settings, options );
    }

    var photo_id = settings["photo_id"];
    var loading_function = settings["loading_function"];

    var loaded_code = '';

    var rand = Math.floor(Math.random()*10000);
    $.ajax({ async: false,  
             url: "/static/html/share_to_fb.html?i="+rand+" #top_level", 
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

    function build_share_fb(div) {
      div.find("#close_fb_share").click(function(e) { e.preventDefault(); div.hide(); });
      div.find("#link_cancel").click(function(e) { e.preventDefault(); div.hide(); });

      if (got_fb_perms) {

        div.find("#link_share").click(function(e) {
          e.preventDefault();
          var comment = div.find("#share_comment").val();
          var photo = div.find("#share_photo").val();
          var ds = { 'comment': comment, 'photo_id':photo };
          loading_function(false);
          var response = ajax_call('/photos/share_fb', ds);
          loading_function(true);
  
          if (response["success"]) {
            div.fadeOut();
            var rso = load_remote("#shared");
            $("body").append(rso);
            rso.fadeIn();
            setTimeout(function() { rso.fadeOut(); }, 1000);
          } else {
            div.fadeOut();
          }
        })

      } else {
        div.find("#facebook_upload").hide();
        div.find("#facebook_connect").show();
      }

      return div;
    }

    var existing_div = false;
    if (settings["div"]) {
      var abi_div = settings["div"];
      existing_div = true;      
    } else { 
      var abi_div = load_remote_tmpl('#share_to_fb_wrapper', { 'photo_id':photo_id });
    }   

    var q = build_share_fb(abi_div);
    if (! existing_div) {
//      loading_function(true);
      $(this).append(q);
      q.show();
    }
};
})( jQuery );
