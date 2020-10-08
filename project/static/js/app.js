$(document).ready(function () {
	$(".btn-have-read").on("click", function(){
		$("#modalBookID").attr('value', '' + this.id);
	});

	$(".btn-tab").on("click", function () {
		$(".btn-tab").removeClass('active');
		this.addClass('active');
	});
});