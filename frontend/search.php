<?php
require("include.php");
if(empty($_GET['filetype']) || empty($_GET['query']))
{
	header("Location: index.php");
	die();
}
$s_query = htmlspecialchars($_GET['query']);
$query = "SELECT Format FROM files GROUP BY `Format`";
$result = mysql_query_cached($query);
$input_boxes = "";
foreach($result->data as $category)
{
	$format = htmlspecialchars($category['Format']);
	
	$checked = "";
	foreach($_GET['filetype'] as $type)
	{
		if($type == $format)
		{
			$checked = " checked";
		}
	}
	
	$inputboxes .= "<input type=\"checkbox\" name=\"filetype[]\" value=\"{$format}\" id=\"type_{$format}\" class=\"type_checkbox\"{$checked}><label for=\"type_{$format}\">{$format}</label>";
}
$inputboxes .= "<input type=\"checkbox\" name=\"filetype_all\" id=\"type_all\" onchange=\"toggle_all();\" checked><label for=\"type_all\"><strong>Select / deselect all</strong></label>";
?>
<!doctype html>
<html>
	<head>
		<title>Cryto Books</title>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>
		<script type="text/javascript" src="script.js"></script>
		<script type="text/javascript" src="jqui.js"></script>
		<link href='http://fonts.googleapis.com/css?family=Lora:400,700|Alice' rel='stylesheet' type='text/css'>
		<link type="text/css" rel="stylesheet" href="style.css">
	</head>
	<body>
		<div class="header">
			<div class="header-logo">
				Cryto Books
			</div>
			<div class="header-search">
				<form method="get" action="search.php">
					<div>
						<input type="text" id="query" name="query" class="query" value="<?php echo($s_query); ?>">
						<button type="submit">Search~</button>
					</div>
					<div>
						<?php echo($inputboxes); ?>
					</div>
					<div class="notes">
						<strong>Notes:</strong> all searches are AND searches - results only appear if they<br> 
						match all terms in any order. A maximum of 100 results is shown.
					</div>
				</form>
			</div>
			<div class="clear"></div>
		</div>
		<div class="promo">
			Appreciate this service? Consider <a href="http://cryto.net/donate/">making a donation</a>!
		</div>
		<div class="results">
			<?php

			$found = false;
			
			$query_parts = explode(" ", $_GET['query']);

			$arr_where = array();
			$arr_type = array();

			foreach($query_parts as $part)
			{
				$s_part = mysql_real_escape_string(str_replace("%", "", $part));
				$arr_where[] = "(`Title` LIKE '%{$s_part}%' OR `Authors` LIKE '%{$s_part}%')";
			}

			foreach($_GET['filetype'] as $filetype)
			{
				$s_filetype = mysql_real_escape_string($filetype);
				$arr_type[] = "`Format` = '{$s_filetype}'";
			}

			$where = implode(" AND ", $arr_where);
			$type = implode(" OR ", $arr_type);

			$query = "SELECT * FROM books WHERE {$where} LIMIT 100";

			if($result = mysql_query_cached($query))
			{
				foreach($result->data as $row)
				{
					$id = $row['Id'];
					$query = "SELECT * FROM files WHERE `BookId` = '$id' AND ({$type})";
					if($res = mysql_query_cached($query))
					{
						$s_title = strip_tags(stripslashes($row['Title']));
						$s_authors = strip_tags(stripslashes($row['Authors']));
						$s_description = strip_tags(stripslashes($row['Description']));
						$s_thumbnail = strip_tags(stripslashes($row['Thumbnail']));
						$s_files = "Download as: ";
						
						if(trim($s_description) == "") 
						{
							$s_description = "There is no description for this book.";
						}
						
						foreach($res->data as $file_row)
						{
							$s_formatname = strip_tags(stripslashes($file_row['Format']));
							$s_formaturl = strip_tags(stripslashes($file_row['Url']));
							
							$s_files .= "<a href=\"{$s_formaturl}\" class=\"format\">{$s_formatname}</a>";
						}
						
						
						echo("<div class=\"item\">
							<div class=\"metadata\" onclick=\"$('.description').hide(); $(this).parent().children('.description').show();\">
								<div class=\"names\">
									<span class=\"title\">
										{$s_title}
									</span>
									<span class=\"authors\">
										{$s_authors}
									</span>
								</div>
								<div class=\"files\">
									{$s_files}
								</div>
								<div class=\"clear\"></div>
							</div>
							<div class=\"description\">
								<img class=\"thumb\" src=\"{$s_thumbnail}\">
								{$s_description}
								<div class=\"clear\"></div>
							</div>
							<div class=\"clear\"></div>
						</div>");
						$found = true;
					}
				}
			}
			
			if($found === false)
			{
				echo("No books were found that match your query.");
			}
			?>
		</div>
	</body>
</html>
