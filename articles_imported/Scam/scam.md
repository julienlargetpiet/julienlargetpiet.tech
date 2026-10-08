
![../../assets/common_files/thumbnails/scam.webp](../../assets/common_files/thumbnails/scam.webp)

Yesterday, I was uploading listings for some fitness equipment I bought during the COVID period on the French equivalent of Craigslist (not [https://www.craigslist.org/area/paris](https://www.craigslist.org/area/paris) lol, but [leboncoin.com](leboncoin.com) ), which I was using for the first time.

So, 13 listings and about four hours later, I received an offer, which I accepted.

And boom: in Leboncoin’s rather terrible chat interface, a very professional-looking sales notification suddenly appeared:

![../../assets/common_files/scam/scam1.jpg](../../assets/common_files/scam/scam1.jpg)

For someone who doesn’t know how the platform works, someone who has never used it before, or who has only ever been paid in cash during an in-person sale, this can look completely legitimate.

After digging a little deeper, you find out that Leboncoin has what is essentially an escrow-like wallet system. The buyer can send the money through Leboncoin, where it is temporarily held for the seller. Once the buyer and seller meet, and the buyer confirms that he is satisfied with the item and want to complete the purchase, the transaction is validated and the money is released to the seller.

If the transaction does not go through because he's not satisfied, the money is returned to the buyer.

At this point, I still hadn’t entered my credit card information anywhere to link the Leboncoin wallet to my bank account.

This actually seemed normal, because Leboncoin apparently only lets you do that once your wallet balance is above €0, which wasn’t the case for me yet. Still, it was confusing, especially because of the very professional-looking sales notification that had appeared earlier.

At that point, I thought the only way to link my bank account was to click on the PDF attached to the notification, which looked like a transaction summary.

So I did.

And this is what it looked like:

![../../assets/common_files/scam/scam2.jpg](../../assets/common_files/scam/scam2.jpg)

“Maybe Leboncoin uses generative AI,” I thought to myself.

Then I clicked on **“Voir les détails”**.

It redirected me to a domain name that, at first glance, looked like it belonged to Leboncoin:

![../../assets/common_files/scam/scam3.jpg](../../assets/common_files/scam/scam3.jpg)

But it didn’t.

In fact, it's just a sub-domain of another domain name (`nouvellevoie.pro`):

[https://leboncoin.nouvellevoie.pro/receive/623046761675](https://leboncoin.nouvellevoie.pro/receive/623046761675)

Then, I clicked on **“Étape 2/2 : obtenir”**.

After that, I was asked to enter my credit card information.

I did it...

Then, the website asked for my bank account balance, which I also entered.

And then it asked me to pay roughly `2/3` of my bank account balance to “verify” my account, claiming that the money would be refunded immediately afterward.

That was finally enough to set off the alarm bells in my naive brain.

So I immediately contacted my bank, reported the card as compromised, and had it blocked.

## Conclusion

What made this scam convincing was not some incredibly sophisticated technical trick. It was the fact that it appeared at exactly the right moment, inside a process I did not know yet, and imitated something that could plausibly exist.

The fake transaction summary looked professional enough, the domain contained `leboncoin`, and the whole flow matched what I expected from a platform using an escrow-like payment system. That was enough to make me lower my guard.

The obvious warning sign only came later, when the website asked me to pay a large fraction of my own bank balance to “verify” my account. At that point, the scam became much easier to recognize.

The main lesson for me is simple: when money is involved, never trust a link just because it looks official or appears at the right moment. Check the actual domain name carefully, and when in doubt, go directly to the service’s official website or application instead of following a link received in a message.

I was lucky enough to realize what was happening before authorizing any payment, but I had already entered my card details. Blocking the card immediately was therefore the safest thing to do.

So yes, even if you are comfortable with computers, know what phishing is, and think you would immediately recognize a scam, context can still make a bad link look surprisingly legitimate.

### Red flags to remember

- A trusted brand name appearing somewhere in a URL does not mean the website belongs to that company. In `leboncoin.nouvellevoie.pro`, the actual domain is `nouvellevoie.pro`.
- Never enter payment information through a link received in a marketplace chat unless you have independently verified the website.
- A legitimate service should not ask you to send a large amount of money to “verify” your bank account.
- If something feels suspicious, open the official website or app yourself instead of following the provided link.
- If you entered your card details on a suspicious website, contact your bank immediately and block the card.
























