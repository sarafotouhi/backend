import React from "react";
import * as pdfjsLib from "pdfjs-dist/build/pdf"
import pdfjsWorker from "pdfjs-dist/build/pdf.worker.entry";
class PdfToText extends React.Component {

	// Constructor
	constructor(props) {
		super(props);

		this.state = {
			TextArray: [],
			renderAgain: false, //this compoenent state renders everything again ocne TextArray is filled with contend
		};
		this.updateTextArray = this.updateTextArray.bind(this);
	}

//--------------------------------------------------------
//this function extract a page from the pdf 
  	async pdfTextExtractor (url){
		console.log("isnide peft extractor ",url);
		const doc = await pdfjsLib.getDocument(url).promise
		const page = await doc.getPage(1) //this line can change which page gets turned into text
		return await page.getTextContent()
	}

//this function extract each line in the extracted page turns into txt string (all in all, the entire page into string Array)
	async getItems(){
		console.log("isnide get ",this.props.url);
		const content = await this.pdfTextExtractor(this.props.url)
		//this.setState({TextArray: await content});
		this.updateTextArray(content.items);
		const items = content.items.map((item) => {
			// console.log(item.str)
			return item
		})
		return items
	}

	updateTextArray(content){
		console.log('UpdatedTextarray', this.state.TextArray )
		this.setState({TextArray: content});
		console.log('UpdatedTextarray', this.state.TextArray )
		this.setState({renderAgain: true})
		
		
	}

	// ComponentDidMount is used to
	// execute the code
	componentDidMount() {
		// if (!this.state.signedUrl) {
			this.getItems()
		//}
		 
	
	}
	
	render() {
		
		return (
			<div>
				{this.state.renderAgain? this.state.TextArray.map(item => <div key={item}>{item.str}</div>)
				: console.log('empty')}
			</div>
      
	);


}
}

export default PdfToText;
