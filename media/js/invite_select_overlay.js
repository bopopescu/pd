(function( $ ){
  $.fn.invite_select_overlay = function(options) {
    var settings = {
      'children':[ { 'id': '267', 'first_name': 'Sheila' }, { 'id': '268', 'first_name': 'Mike' } ] ,   

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

    var loaded_code = '';

    var rand = Math.floor(Math.random()*10000);
    
    $.ajax({ async: false,  
             url: "/static/html/invite_select_overlay.html?i="+rand+" #top_level", 
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

    function build_invite_select_overlay(div) { 

      var invite_choice_container = div.find("#invite_choice_container");      
      for (child_idx in settings["children"]) {
         var child = settings["children"][child_idx];
         var ic = load_remote_tmpl('#invite_choice_wrapper', child);
         ic.find("a.select_invite").click(function(e) {
            e.preventDefault();
            var choice = $(this).attr('rel');
            var parent_li = $(this).parent("li");
            parent_li.siblings("li").removeClass("current");
            parent_li.addClass("current");
            var hidden_input = parent_li.siblings(".invite_choice");
            hidden_input.val(choice);
         });
         invite_choice_container.append(ic);
      }
     

      div.find("#submit").click(function(e) {
        e.preventDefault();
        var icc = $("#invite_choice_container");

        var child_choice_arr = [];
        icc.find(".invite_choice_span").each(function() {

          var ics = $(this);

          var child_id = ics.find(".child_id").val();
          var child_choice = ics.find(".invite_choice").val();
          var child_choice_arr_item = child_id + ":" + child_choice;

          child_choice_arr.push(child_choice_arr_item);
        });                

        var ds = { 'choices': child_choice_arr };
        var response = ajax_call('/playdates/set_invite_choices', ds);

        div.remove();
      });

      return div;
    }

    var ds = {}

    var div = load_remote_tmpl('#invite_select_overlay_wrapper', ds);

    var q = build_invite_select_overlay(div);

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
