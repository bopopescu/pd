var child_choice_template = '<li><a href="#" class="" title="${id}">${fname}</a></li>';
var day_template = '<div class="day_wrap"><div class="day">${day} <sup>${suffix}</sup></div><div class="weekday" style="font-size:90%">${dow}</div>';
var cc_template = '<span><div class="calendar_top"><h2 class="date">${month}</h2><ul id="child_choice"></ul><a href="/schedule/view/" id="view_all" class="view_all">View / Edit Calendar</a> </div><div class="datetime"></div><div class="calendar_bottom"><ul id="event_list"></ul></div></span>';


(function( $ ){
  $.fn.condensed_calendar = function(options) {

    var settings = {
    };

    
    if ( options ) { 
      $.extend( settings, options );
    }

    // var mydiv = $.tmpl(child_choice_template, { "id":33, "fname":"Vicky" });

    var get_events = settings["get_events"];
    var condensed_calendar_html = $.tmpl(cc_template, { 'month':settings['month'] }) 

    var days_div = condensed_calendar_html.find("div.datetime");
    for (day_idx in settings["days"]) {
      var day_html = $.tmpl(day_template, settings["days"][day_idx]);
      days_div.append(day_html);
    }

    var child_div = condensed_calendar_html.find("#child_choice");
    var event_list_ul = condensed_calendar_html.find("#event_list");
    for (child_idx in settings["children"]) {
      var child = settings["children"][child_idx];
      var child_li = $.tmpl(child_choice_template, child);
      if (child["id"] == settings["current_child_id"]) {
        child_li.find("a").addClass('current schedule_current_child');
      } else {
        child_li.find("a").addClass('schedule_not_current_child');
      }
      if (child_idx > 0 ) {
        child_li.prepend('| ');
      }
      child_div.append(child_li);
    }

    function populate_event_list(container,events) {
      container.empty();
      var days_li = [];
      var any_events = false;

      for (day_index in events) {
        var day_li = $("<li></li>");
        var day_ul = $("<ul></ul>");
    
        for (event_idx in events[day_index]) {
          any_events = true;
          var event = events[day_index][event_idx]
          var event_li = '';
          if (event["direct_url"]) {
            event_li = $("<li><a class='green' href='" + event["direct_url"] + "'><span class='time'>"+event["start"]+"</span><span>"+event["summary"]+"</span></a></li>");            
          } else {
            event_li = $("<li><span class='time'>"+event["start"]+"</span><span>"+event["summary"]+"</span></li>");
          }
          day_ul.append(event_li);
        }         
        day_li.append(day_ul);
        days_li.push(day_li);
      }

      if (any_events) {
        for (didx in days_li) {
          container.append(days_li[didx]);
        }
      } else {
        var zero_li = $('<li class="zero"><p class="title">No plans yet?</p><p>Click the <a href="/playdates/new">Make a Plan</a> button or <a class="view_all" href="/schedule/view/">Edit Calendar</a> link to get started!</p></li>');
        container.append(zero_li);
      }
    }
    
    $("a.schedule_not_current_child").live('click', function(e) {
      e.preventDefault();
      var child_id = $(this).attr('title');
      var child_clicked = $(this);
      
      get_events(child_id, function(data) {
        events = data; 
        populate_event_list(event_list_ul,events);
        var current_child = $("#child_choice li a.schedule_current_child");
        current_child.removeClass("schedule_current_child");
        current_child.removeClass("current");
        current_child.addClass("schedule_not_current_child");
        child_clicked.removeClass("schedule_not_current_child");
        child_clicked.addClass("schedule_current_child");        
        child_clicked.addClass("current");
        condensed_calendar_html.find(".view_all").attr('href',schedule_view_base_url+child_id+'/');
      });
    });

    var child_id = child_div.find("li a.schedule_current_child").attr('title');
    var schedule_view_base_url = '/schedule/view/';  
    condensed_calendar_html.find(".view_all").attr('href',schedule_view_base_url+child_id+'/');

    get_events(child_id, function(data) {
        events = data; 
        populate_event_list(event_list_ul,events);
    }); 

    $(this).append(condensed_calendar_html);


};
})( jQuery );

