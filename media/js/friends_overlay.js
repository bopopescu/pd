(function( $ ){
  $.fn.friends_overlay = function(options) {

    var settings = {
      'get_data':function() { console.log('getting data'); },
      'loading_function':function() { }
    };

    
    if ( options ) { 
      $.extend( settings, options );
    }

    var loading_function = settings["loading_function"];
    var get_data =  settings["get_data"];
    var next_step = settings["next_step"];
    var children = settings["children"];
    var fname = settings["fname"];
    var already_added = {};

    var loaded_code = '';
// preload required html
    $.ajax({ async: false,  
             url: "/static/html/friends_overlay_div.html #top_level", 
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

    function add_done_div() {
        var success = $("<div class=\"success_section\">Has been Added Successfully</div>");
        return success;
    }
  
    function populate_users_container(container, add_to_playlist_div, playdation_friends, start_index, number_to_display) {
      var i = start_index;
      var end_index = start_index + number_to_display; 
      container.empty();
  
      while (i < end_index) {
        if (! playdation_friends[i]) {
          break;         
        }
  
        var user = playdation_friends[i]["user"]
        var child = playdation_friends[i]["child"]
  
        var user_data ={
          'user_fname':user["first_name"], 
          'user_lname':user["last_name"],
          'user_url':user["small_profile_pic"],
          'user_id':user["id"],
          'child_age':child["age"],
          'child_gender':child["gender"],
          'child_id':child["id"],
        }
          
        var user_div = load_remote_tmpl('#user_template', user_data, function() { });
        user_div.find("img.user_pic").attr("src", user_data["user_url"]);
        var to_child = user_data["child_id"];
        var to_user = user_data["user_id"];
  
        if (already_added[to_user+"-"+to_child]) {
          var atpd = add_done_div();
          user_div.find(".user_friend_form").append(atpd);
        } else {
          var atpd = add_to_playlist_div.clone(true);  
          user_div.find(".user_friend_form").append(atpd);
        }
        container.append(user_div);
        i=i+1;
      }        
    }

  

    function construct_add_to_playlist_div(children) {
      var form_box = load_remote_tmpl('#form_box', {}, function() { });
            
      if (children.length > 1) {
        var child_select = load_remote_tmpl('#child_select', {}, function() { });
        for (child in children) {
          var child_option =$('<option value="'+children[child]["child_id"]+'">'+children[child]["child_fname"]+'</option>');          
          child_select.append(child_option);
        }
        form_box.find(".input_btn").prepend("<br>").prepend(child_select);
      }

  
      form_box.find(".input_btn").click(function(event) {
        event.preventDefault();
        var target = $(event.target);
        var user_friend_form = target.parents(".user_friend_form");
        
        var to_child = user_friend_form.find(".to_child").val();
        var to_user = user_friend_form.find(".to_user").val();
        var pd_friend_index = user_friend_form.find(".pd_index").val();
        var from_child = children[0]["child_id"]; 
  
        if (children.length > 1) {
          from_child = user_friend_form.find(".child_select").find(":selected").val();        
        }

        var ds = {
            "to_user": to_user,
            "to_child": to_child,
            "from_child": from_child,
            "source": "friends_overlay",
        }

        response = send_invite(ds);
  
        if (response["success"] == "true") {
          var success = add_done_div();
          target.parents(".form_box").replaceWith(success);        
          already_added[to_user+"-"+to_child] = true;
        } else {
          var failure = $("<div class=\"success_section\">"+response["message"]+"</div>");
          target.parents(".form_box").replaceWith(failure);        
        }
  
      });
      return(form_box);
    }

    function construct_users_container(container, add_to_playlist_div, playdation_friends, done_skip) {
      container.empty();
      var current_start_index = 0;
      populate_users_container(container, add_to_playlist_div, playdation_friends ,0,3);
  
      var left_arrow = container.siblings("div#arrow_div").find("#left_arrow");
      var right_arrow = container.siblings("div#arrow_div").find("#right_arrow");
      left_arrow.hide();
  
      if (playdation_friends.length < 3) {        
        right_arrow.hide();
      }
  
      left_arrow.click(function(event) {
        var target = $(event.target);    
        current_start_index = current_start_index - 3;
        populate_users_container(container, add_to_playlist_div, playdation_friends,current_start_index,3)
        right_arrow.show();
        if (current_start_index < 1) {
          left_arrow.hide();      
        }
      });
  
      right_arrow.click(function(event) {
        var target = $(event.target);    
        current_start_index = current_start_index + 3;
        populate_users_container(container, add_to_playlist_div, playdation_friends,current_start_index,3)
        left_arrow.show();
        if (current_start_index +4  > playdation_friends.length) {
          right_arrow.hide();      
        }
      });
      var link_done = container.siblings("div.link_buttons").find("#link_done");
      var link_skip = container.siblings("div.link_buttons").find("#link_skip"); 
      link_done.click(function(event) {
        event.preventDefault()
        container.parents('#possible_friends').hide();
        done_skip()
      });
      link_skip.click(function(event) {
        event.preventDefault()
        container.parents('#possible_friends').hide();
        done_skip()
      });
    }


    function build_friends_overlay(playdation_friends) {
      var current_start_index = 0;
      var friends_overlay = load_remote_tmpl('#possible_friends_wrapper', { 'fname':fname }, function() { });
      var user_container = friends_overlay.find("#user_container");
      var add_to_playlist_div = construct_add_to_playlist_div(children);
      construct_users_container(user_container, add_to_playlist_div, playdation_friends, next_step);

      friends_overlay.find('#close_friends_overlay_button').click(function(event) {
        event.preventDefault()
        friends_overlay.hide();        
      });

      return friends_overlay;
    }

    loading_function(false);

    playdation_friends = []
    get_data( function(data) {
      if (data["success"]) {
        playdation_friends = data["playdation_friends"];
        if (playdation_friends.length) {
          var q = build_friends_overlay(playdation_friends);
          loading_function(true);
          q.hide();
  
          $("body").append(q);
  
          var lw = q.find(".lightbox_wrapper");
          lw.css('top', 100);
      
          var maybe_new_height = 100 + lw.outerHeight();
      
          var set_height = $(document).height();
          if (maybe_new_height > set_height) {
            set_height = maybe_new_height;
          }   
      
          q.height(set_height);
          q.show();
        } else {
          loading_function(true);          
          next_step();  
        }
      } else {
        loading_function(true);          
        next_step();
      }
    });

};
})( jQuery );
