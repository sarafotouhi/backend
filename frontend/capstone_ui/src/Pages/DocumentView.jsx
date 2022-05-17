import React from "react";
import DocumentDisplay from "./DocumentDisplay.jsx"
/*
Description: This class fetches signedUrl for the document from AWS server, then used this link to fetch doc object from the S3 bucket
*/
class DocumentView extends React.Component {

	// Constructor
	constructor(props) {
		super(props);

		this.state = {
      		signedUrl: "",
		};
		
        this.setSignedUrl = this.setSignedUrl.bind(this);
		this.signedUrl = this.signedUrl.bind(this);
	}

	setSignedUrl(url){
		this.setState({signedUrl: url})
	}

	//This function gets the signedUrl from AWS using which the document is fetched from the AWS bucket.
	signedUrl() {
		var AWS = require('aws-sdk');
		AWS.config.update({ 
			accessKeyId: process.env.REACT_APP_ACCESS_KEY,
			secretAccessKey: process.env.REACT_APP_SECRET_KEY,
			region: 'us-east-1',
		});

		const s3 = new AWS.S3()
		const myBucket = "capstone-data-bucket"
		const myKey = "test-organization/test-workspace/contracts/part of contract.pdf"
		const signedUrlExpireSeconds = 60 * 15
		const url = s3.getSignedUrl('getObject', {Bucket: myBucket, Key: myKey, Expires: signedUrlExpireSeconds});
		this.setSignedUrl(url);
  }

	// ComponentDidMount is used to execute the code
	componentDidMount() {
		if (!this.state.signedUrl) {
			this.signedUrl();
		}
		 
	
	}
	
	render() {
		
		const {signedUrl} = this.state;
		if (!signedUrl) 
			return <div>
				<h1> Loading.... </h1> 
			</div> ;

		return (
			<div>
				{this.state.signedUrl? <DocumentDisplay url={this.state.signedUrl}/> : null}
			</div>
	);


}
}

export default DocumentView;
;
