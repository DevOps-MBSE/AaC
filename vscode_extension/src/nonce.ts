/**
* Provide a "nonce" value for allowing Content-Security Policy to load inline scripts.
* https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/nonce
*/
export function getNonce() {

	let text = '';
	const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
	for (let i = 0; i < 32; i++) {
		text += possible.charAt(Math.floor(Math.random() * possible.length));
	}
	return text;
}
