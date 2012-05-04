function toggle_all()
{
	if($('#type_all')[0].checked == true)
	{
		$('.type_checkbox').attr('checked', true);
	}
	else
	{
		$('.type_checkbox').attr('checked', false);
	}
}
