var fb_friends = false;
var key_list = {};
var e_friends = false;

var fb_friends_list = '<ul id="fb_friends_ul" class="friends_list">';
var fb_friends_ul = '';
var got_fb_perms = false;
var got_fb = false;
var ds = { };
ajax_async_call('/playdates/get_fb_friends/', ds, function(data) {
  fb_friends = data["fb_friends"];
  got_fb = data["got_fb"];
  got_fb_perms = data["got_fb_perms"];

  if (! got_fb) {
      fb_friends_list = '<div class="friends_zero"><p class="title">Facebook account not connected.</p><p>You have not yet connected your Facebook account to your Playdation account. Please connect your facebook account <a href="/account/connect_fb/pdi/">here</a>.</p></div>';
  } else {
    for (pdi in fb_friends) {
      key_list[fb_friends[pdi]["key"]] = fb_friends[pdi];
    }

    for (fr_idx in fb_friends) {
       var friend = fb_friends[fr_idx];
       var li = '<li class="'+friend["selected"]+' selectable_parent" ><input type="hidden" class="key" value="'+friend["key"]+'"><a href="#" class="selectable" title="'+friend["tip"]+'"> <img src="'+friend["small_profile_pic"]+'" alt="" width="50" height="50" />'+friend["name"]+' </a> </li>'
       fb_friends_list = fb_friends_list + li;
    }      
  
    fb_friends_list = fb_friends_list + '</ul>';
  }
  fb_friends_ul = $(fb_friends_list);
});

ajax_async_call('/playdates/get_e_friends/', ds, function(data) {
  e_friends = data;
  for (pdi in e_friends) {
    key_list[e_friends[pdi]["key"]] = e_friends[pdi];
  }
});




(function( $ ){
  $.fn.pd_inviter = function(options) {
    var settings = {
      'callback':function(selected) { console.log(selected); },
      'current_list':{},
    };

    if ( options ) { 
      $.extend( settings, options );
    }

    var loaded_code = '';

    var rand = Math.floor(Math.random()*10000);
    $.ajax({ async: false,  
             url: "/static/html/pd_inviter.html?i="+rand+" #top_level", 
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

    var pd_friends = false;
    
    function get_pd_friends() {
       
      if (! pd_friends) {
        ds = { 'oc': settings["oc"] };
        pd_friends = ajax_call('/playdates/get_oc_pd_friends/', ds);
        for (pdi in pd_friends) {
          key_list[pd_friends[pdi]["key"]] = pd_friends[pdi];
        }
      }
      return pd_friends;
    }

//    var fb_friends = false;
    function get_fb_friends() {
       
      if (! fb_friends) {
        ds = { };
        fb_friends = ajax_call('/playdates/get_fb_friends/', ds);
        for (pdi in fb_friends) {
          key_list[fb_friends[pdi]["key"]] = fb_friends[pdi];
        }
      }
      return fb_friends;
    }

    function get_email_friends() {
      if (! e_friends) {
        ds = { };
        e_friends = ajax_call('/playdates/get_e_friends/', ds);
        for (pdi in e_friends) {
          key_list[e_friends[pdi]["key"]] = e_friends[pdi];
        }
      }
      return e_friends;
    }

    function get_selected() {     
      return all_selected;
    }

    function add_key(key, item) {
      all_selected[key] = item;
    }

    function remove_key(key) {
      delete all_selected[key];
    }

    function validate_email(email) {
      var reg = /^([A-Za-z0-9_\-\.\+])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,3})$/;
      return (reg.test(email));
    }

    function render_current_invitees(current) {
      $.each( current, function(index, invitee) {
        key_list[invitee["key"]] = invitee;
        toggle_invitee(invitee["key"]);
      });
    }

    function toggle_invitee(key) {
      var pds = get_selected();
      var li_tmpl = '<li><input type="hidden" class="key" value="${key}"><a href="#" class="remove_invitee">${name}</a><a href="#" class="remove_invitee"><img src="/static/images/bg_del.png" alt="" width="9" height="9" /></a></li>';

      if ( ! pds[key] ) {
         var ul = div.find("#current_invitees");
         if (key_list[key]) {
           var invitee = key_list[key];
         } else {

           var name = key;
           if ( key.length > 15) {
             name = key.substr(0,15) + '..';
           };

           var invitee = { 'name':name, 'key':key, 'tip':key, };
         }

         var li = $.tmpl(li_tmpl, invitee);
         ul.append(li);
         add_key(key, invitee);

         li.find("a.remove_invitee").click(function(e) {
           e.preventDefault();
           var parent_li = $(this).parent();
           var r_key = parent_li.find(".key").val();
           remove_key(r_key);
           parent_li.remove();
         });
      }
    }

    var pd_div_done = false;


    function populate_pd(container) {
      if (! pd_div_done) {
        var pdf = [];
        if (settings["oc"].length > 0) {
          pdf = get_pd_friends();
        }

        if (settings["oc"].length == 0) {
            var pd_empty_div = '<div class="friends_zero"><p class="title">Which kids are hosting the playdate?</p><p>This area gets populated with friends of the kids that are hosting the playdate. </p></div>';
            container.append(pd_empty_div);
        } else if (pdf.length == 0) {
            var pd_empty_div = '<div class="friends_zero"><p class="title">No Playdation friends.</p><p>You have not yet connected with any of your friends on Playdation. Use the other tabs to invite your friends via Facebook or email.</p></div>';
            container.append(pd_empty_div);
        } else {
            var pd_friends_list = '<ul class="friends_list">';  
	        for (fr_idx in pdf) {
	           var friend = pdf[fr_idx];
	           var li = '<li class="'+friend["selected"]+' selectable_parent" ><input type="hidden" class="key" value="'+friend["key"]+'"><a href="#" class="selectable" title="'+friend["tip"]+'"> <img src="'+friend["small_profile_pic"]+'" alt="" width="50" height="50" />'+friend["name"]+' </a> </li>'
	           pd_friends_list = pd_friends_list + li;
	        }      
	
	        pd_friends_list = pd_friends_list + '</ul>';
	        container.append(pd_friends_list);
        }

        pd_div_done = true;
  
        container.find("a.selectable").click(function(e) {
          e.preventDefault();
          var parent_li = $(this).parent("li.selectable_parent");
          var key = parent_li.find(".key").val();
          toggle_invitee(key);
        })
      }
    }

    var fb_div_done = false;
    function populate_fb(container) {
      if (! fb_div_done) {
        container.append(fb_friends_ul);
        container.find("a.selectable").click(function(e) {
          e.preventDefault();
          if (got_fb_perms ) {
            var parent_li = $(this).parent("li.selectable_parent");
            var key = parent_li.find(".key").val();
            toggle_invitee(key);
          } else {
             $("#fb_friends_ul").replaceWith($('<div class="friends_zero"><p class="title">Oops. We need your help.</p><p>In order to invite your friends we need you to grant us one additional Facebook permission.  Please click <a href="/account/connect_fb/pdip/">here</a>.</p></div>'));
          }

          // check_for_facebook_perms($(this),
          //   function(element) {
          //     if (! got_fb_perms) {
          //       got_fb_perms = true;
          //       ajax_async_call('/profiles/set_got_fb_stream_publish/', { }, function(data) { } );
          //     }
          //     var parent_li = element.parent("li.selectable_parent");
          //     var key = parent_li.find(".key").val();
          //     toggle_invitee(key);
          //   },
          //   function(element) {
          //     alert("Sorry. We can't invite from Facebook without the extra permissions");
          //   }
          // );


        });

        fb_div_done = true;
      }
    }

    function populate_email(container) {
      var ul = container.find("ul.friends_list");
      ul.empty();
      var ef = get_email_friends();

      var li_tmpl = '<li class="selectable_parent"><input type="hidden" class="key" value="${key}"> <button type="button" class="selectable">Select</button><label>&nbsp;&nbsp; ${tip}</label></li>'

      for (fr_idx in ef) {
         var friend = ef[fr_idx];
         var li = $.tmpl(li_tmpl, friend);
         ul.append(li);
      }      

      container.find("#new_email_address").keypress(function(e){
          if (e.which == 13) { 
            $("#save_email_address").trigger('click');
            return false;
          } 
      });

      container.find("#save_email_address").click(function(e) {
        var key = container.find("#new_email_address").val();

        if (validate_email(  key ) ) {
          toggle_invitee(key);
          $("#new_email_address").val('');
        }    
      });

      container.find(".selectable").click(function(e) {
        var parent_li = $(this).parent("li.selectable_parent");
        parent_li.toggleClass('selected');
        var key = parent_li.find(".key").val();
        toggle_invitee(key);
      })
    }



    function render_tab(activeTab) {
        if (activeTab == '#pd') {
          populate_pd(div.find(activeTab));
        } else if (activeTab == '#fb') {
          populate_fb(div.find(activeTab));
        } else {
          populate_email(div.find(activeTab));
        }
    }

    function build_pd_inviter(div) {

      var to_parent = div.find("#to_parent"); 

      div.find(".close_pd_inviter").click(function(e) {
        e.preventDefault();       
        div.fadeOut();
      });


      div.find(".tab_content").hide(); //Hide all content
      var first_tab = div.find("ul.tabs li:first");
      var activeTab = first_tab.find("a").attr("href");
      render_tab(activeTab);

      render_current_invitees(current_selected);


      first_tab.addClass("active").show(); //Activate first tab
      div.find(".tab_content:first").show(); //Show first tab content
      
      //On Click Event
      div.find("ul.tabs li").click(function() {
        var activeTab = $(this).find("a").attr("href");
        div.find("ul.tabs li").removeClass("active"); //Remove any "active" class
        $(this).addClass("active"); //Add "active" class to selected tab
        div.find(".tab_content").hide(); //Hide all tab content
        div.find(activeTab).fadeIn(); //Fade in the active content
        render_tab(activeTab);

        return false;
      });

      div.find("#save_guest_list").click(function(e) {
        e.preventDefault();       
        div.fadeOut();
        settings["callback"](get_selected());
      });
      
      return div;      
    }

    var ds = {
      'name':settings["name"],
      'to_user_id':settings["to_user_id"],
    };

    var all_selected = {};
    var current_selected =  settings["current_list"];
    
    var div = load_remote_tmpl('#pd_inviter_wrapper', ds);

    var q = build_pd_inviter(div);

    q.hide();
    $("body").append(q);

    var lw = q.find(".lightbox_wrapper");
    lw.css('top',$(window).scrollTop() + 100);

    var maybe_new_height = $(window).scrollTop() + 100 + lw.outerHeight();

    var set_height = $(document).height();
    if (maybe_new_height > set_height) {
      set_height = maybe_new_height;
    }   

    q.height(set_height+400);

    q.fadeIn();

  };
})( jQuery );
