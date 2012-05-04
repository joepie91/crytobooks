<?php 
require("include.php"); 
$query = "SELECT Format FROM files GROUP BY `Format`";
$result = mysql_query_cached($query);
$input_boxes = "";
foreach($result->data as $category)
{
	$format = htmlspecialchars($category['Format']);
	$inputboxes .= "<input type=\"checkbox\" name=\"filetype[]\" value=\"{$format}\" id=\"type_{$format}\" class=\"type_checkbox\" checked><label for=\"type_{$format}\">{$format}</label>";
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
		<link href='http://fonts.googleapis.com/css?family=Lora:400,700|Alice' rel='stylesheet' type='text/css'>
		<link type="text/css" rel="stylesheet" href="style.css">
	</head>
	<body>
		<div class="wrapper">
			<form method="get" action="search.php">
				<div class="logo">
					Cryto Books
					<div class="slogan">
						Free book search engine.
					</div>
				</div>
				<div class="searchbar">
					Query:
					<input type="text" id="query" name="query">
				</div>
				<div class="searchoptions">
					<?php echo($inputboxes); ?>
				</div>
				<div class="searchbutton">
					<button type="submit">
						Search~
					</button>
				</div>
			</form>
			<div class="copyright">
				The Cryto Books database is automatically generated from online ebook sources, and entries are not manually reviewed before becoming visible. Cryto Books does not host any files
				itself - it is merely a search engine. If you wish to see materials that you own the copyright to removed from the index, contact jamsoftgamedev@gmail.com.
			</div>
			<div class="links">
				<h1>Other websites you might find useful:</h1>
				
				<strong><a href="http://calibre-ebook.com/">Calibre Ebook Manager</a></strong> - Free ebook management software that can organize and convert various ebook formats. If it's on Cryto Books, Calibre can read it.<br>
				<strong><a href="http://www.gutenberg.org/">Project Gutenberg</a></strong> - Free digitized books with expired copyright in various formats.<br>
				<strong><a href="http://books.google.com/">Google Books</a></strong> - Free book search - both free (public domain) books and snippets of copyrighted books.<br>
				<strong><a href="http://www.wikibooks.org/">Wikibooks</a></strong> - Collaborative writing of educational textbooks, wiki-style.
			</div>
		</div>
	</body>
</html>
