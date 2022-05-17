import React from "react";
/*
Description: This function takes ginedUrl for the document, and display it using iframe
*/
export default function DocumentDisplay({url}) {
		return (
				<iframe
        		src={url}
				title= " "
				width="100%"
				height="900"
				></iframe>
	);


}