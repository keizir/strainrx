'use strict';

$(document).ready(function(){
  $(window).scroll(function(){
    if($(window).scrollTop() <= 100){
      $(".navbar-fixed-top").removeClass("fixed")
    }
    else{
      $(".navbar-fixed-top").addClass("fixed")
    }
  });
  $(".navbar-toggle").click(function()
  {
    $(".navbar-collapse").toggle();
  });
  $(".testimonial-carousel").slick({
    infinite: true,
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: false,
    arrows: true,
    prevArrow: $(".testimonial-carousel-controls .prev"),
    nextArrow: $(".testimonial-carousel-controls .next")
  });
})