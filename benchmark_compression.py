import bz2
import csv
import platform
import sys
import time
import zlib

import blosc
import lz4.frame
import requests
import snappy
from tqdm import tqdm


def run():
    url_list = [
        'https://www.helmet.beam.vt.edu/bicycle-helmet-ratings.html',
        'https://mikkel.hoegh.org/2019/08/29/how-software-made-me-loathe-my-luxury-car',
        'https://jobs.lever.co/pachyderm/', 'https://consider.co/groups',
        'https://sinapticas.com/2019/08/29/beyond-reason-the-mathematical-equation-for-unconditional-love/',
        'https://github.com/rnd-team-dev/plotoptix/tree/master/examples/3_projects/moon',
        'https://www.theguardian.com/books/2019/aug/24/is-the-political-novel-dead',
        'https://www.bloomberg.com/news/articles/2019-08-29/dalio-s-flagship-hedge-fund-gets-burned-by-wrong-way-rate-bets',
        'https://connective.dev', 'https://lunchmoney.cc',
        'https://www.businessinsider.com/juul-ceo-dont-vape-long-term-effects-unknown-2019-8', 'https://texnique.xyz',
        'https://medium.com/solo-io/api-gateways-are-going-through-an-identity-crisis-d1d833a313d7',
        'https://news.ycombinator.com/item?id=20831105', 'https://www.apple.com/apple-events/',
        'https://www.hackerrank.com/tests/7j6a5mhn6lb/78766bda888f6c08605024290c926550', 'https://jmap.io/',
        'https://github.com/TankerHQ/sdk-js/tree/master/packages/filekit',
        'https://actu.epfl.ch/news/universal-algorithm-set-to-boost-microscopes/',
        'http://isohedral.ca/a-molecular-near-miss/',
        'https://www.lego.com/en-gb/aboutus/news-room/2019/august/audio-and-braille-instructions/',
        'https://techcrunch.com/2019/08/28/uber-proposes-policy-that-would-pay-drivers-a-minimum-wage-of-21-per-hour/',
        'https://en.wikipedia.org/wiki/CS_Alert_(1890)', 'https://stallman.org/google.html',
        'https://brave.com/wikipedia-verified-publisher/', 'https://www.shoptiques.com/careers/jobs?id=csm-pos',
        'https://0x0f0f0f.github.io/posts/2019/08/building-a-raspberry-pi-3b-full-keyboard-handheld.-part-1/',
        'https://zengo.com/qr-code-degenerators/', 'https://www.historytoday.com/history-matters/beard-maketh-man',
        'https://www.apple.com/newsroom/2019/08/apple-offers-customers-even-more-options-for-safe-reliable-repairs/',
        'https://arxiv.org/abs/1908.10693', 'https://blog.regehr.org/archives/1687',
        'https://www.nybooks.com/daily/2019/08/28/from-the-battlefield-to-little-women/',
        'https://www.1843magazine.com/culture/look-closer/stick-em-up-a-surprising-history-of-collage',
        'https://blog.mozilla.org/blog/2019/08/29/thank-you-chris/',
        'https://blog.dominodatalab.com/deep-reinforcement-learning/',
        'https://blog.theodo.com/2019/08/event-driven-architectures-rabbitmq/',
        'https://cointelegraph.com/news/portugal-tax-authority-bitcoin-trading-and-payments-are-tax-free/',
        'https://github.com/codejamninja/react-ast',
        'https://uxdesign.cc/tooltips-your-secret-weapon-for-improving-deature-discovery-e1c380562f2e',
        'http://blogs.perl.org/users/ovid/2019/08/is-perl-6-being-renamed.html',
        'https://www.atlasobscura.com/articles/m-h-type-foundry-san-francisco', 'https://zepel.io',
        'https://www.marketwatch.com/articles/apple-ceo-tim-cook-sells-apple-stock-51567009228',
        'https://blog.licensezero.com/2019/08/26/but-you-said.html',
        'https://www.wsj.com/articles/jim-mattis-duty-democracy-and-the-threat-of-tribalism-11566984601?mod=rsswn',
        'https://readbtc.com/blockchain-explorer-guide/',
        'https://lists.gnu.org/archive/html/emacs-devel/2019-08/msg00577.html',
        'https://publicdomainreview.org/2018/01/24/the-dreams-of-an-inventor-in-1420/',
        'http://earth.nautil.us/article/429/the-strange-blissfulness-of-storms',
        'http://worrydream.com/refs/Brooks-NoSilverBullet.pdf', 'https://particlebites.com/?p=6227',
        'https://www.bbc.co.uk/news/science-environment-49486980',
        'https://decoded.avast.io/janvojtesek/putting-an-end-to-retadup-a-malicious-worm-that-infected-hundreds-of-thousands/',
        'https://www.roadandtrack.com/car-culture/a28843412/jessi-combs-killed-in-land-speed-record-crash/',
        'https://www.cnbc.com/2019/08/29/hong-kong-protests-chinese-pla-sends-new-military-troops-into-sar.html',
        'https://medium.com/@Razican/learning-simd-with-rust-by-finding-planets-b85ccfb724c3',
        'https://lareviewofbooks.org/article/literary-economy-on-the-routledge-companion-to-literature-and-economics/',
        'https://www.streak.com/offices/vancouver',
        'http://timharford.com/2019/08/what-we-get-wrong-about-meetings-and-how-to-make-them-worth-attending/',
        'https://medium.com/@mmathieum/google-just-deleted-my-nearly-10-year-old-free-open-source-android-app-7fbc52edc50a',
        'https://feross.org/funding-experiment-recap/',
        'https://ai.googleblog.com/2019/08/exploring-weight-agnostic-neural.html',
        'https://www.youtube.com/watch?v=udlMSe5-zP8',
        'https://bittersoutherner.com/william-ferris-the-man-who-shared-our-voices',
        'https://people.kernel.org/metan/towards-parallel-kernel-test-runs',
        'https://www.kaspersky.com/blog/camscanner-malicious-android-app/28156/',
        'https://pelotonmagazine.com/gear/bontragers-new-wavecel-bests-mips-at-concussion-prevention/',
        'https://www.nature.com/articles/d41586-019-02586-5',
        'https://www.eejournal.com/article/ibm-gives-away-powerpc-goes-open-source/',
        'https://ryanbigg.com/2019/08/can-apple-please-design-a-laptop-that-has-a-functional-keyboard-for-the-love-of-all-that-is-precious',
        'https://www.hkispa.org.hk/139-urgent-statement-of-hkispa-on-selective-blocking-of-internet-services.html',
        'https://www.hongkongfp.com/2019/08/28/hong-kong-democrat-says-emergency-legislation-akin-martial-law-trade-minister-offers-reassurances/',
        'https://www.apptorium.com/sidenotes', 'https://www.nytimes.com/2019/08/28/opinion/vegan-food.html',
        'https://www.bbc.co.uk/news/uk-england-london-49482840',
        'https://techcrunch.com/2019/08/28/readme-scores-9m-series-a-to-help-firms-customize-api-docs/',
        'https://blog.coursera.org/coursera-introduces-hands-on-learning-with-coursera-labs/',
        'https://pipedream.com/@marc/google-alerts-for-hacker-news-p_jmCzVJ/readme',
        'https://arstechnica.com/science/2019/08/16-bit-risc-v-processor-made-with-carbon-nanutubes/',
        'https://angel.co/l/2hgzaS', 'https://github.com/sharkdp/pastel',
        'https://theconversation.com/how-to-keep-buildings-cool-without-air-conditioning-according-to-an-expert-in-sustainable-design-121004',
        'https://www.theverge.com/2019/8/28/20836855/reverse-location-search-warrant-dragnet-bank-robbery-fbi',
        'https://devblogs.microsoft.com/typescript/announcing-typescript-3-6/',
        'http://grr.crankybill.com/2019/02/whats-a-gallon.html',
        'https://www.freightwaves.com/news/shipping-wind-turbines-is-not-a-breeze',
        'https://slatestarcodex.com/2019/08/27/book-review-reframing-superintelligence/',
        'https://spectrum.ieee.org/the-institute/ieee-member-news/software-engineering-grads-lack-the-skills-startups-need',
        'https://techcrunch.com/2019/08/28/india-foreign-direct-investment-fdi-rules-apple/',
        'https://techcrunch.com/2019/08/27/border-deny-entry-united-states-social-media/',
        'https://www.nytimes.com/2019/08/28/us/politics/us-iran-cyber-attack.html',
        'https://www.theatlantic.com/magazine/archive/1982/02/have-you-ever-tried-to-sell-a-diamond/304575/',
        'https://techcrunch.com/2019/08/28/microsoft-wants-to-bring-exfat-to-the-linux-kernel/',
        'https://www.texasmonthly.com/the-culture/cedar-choppers-once-ruled-texas-hill-country/',
        'https://cloudblogs.microsoft.com/opensource/2019/08/28/exfat-linux-kernel/',
        'https://www.reifyworks.com/writing/2019-08-26-a-most-software-companies', 'http://apple1.smartykit.org/',
        'https://www.vice.com/en_us/article/9kxe87/rich-families-are-legally-separating-from-their-kids-to-pay-less-for-college',
        'https://www.newyorker.com/magazine/2019/09/02/are-spies-more-trouble-than-theyre-worth',
        'https://zerocater.com/about/careers/?gh_jid=1749421',
        'https://lithub.com/the-death-of-alexander-the-great-one-of-historys-great-unsolved-mysteries/',
        'https://www.moderntreasury.com/journal/what-happens-when-you-ach-a-dead-person',
        'https://gcc.gnu.org/bugzilla/show_bug.cgi?id=90949',
        'https://internals.rust-lang.org/t/machine-learning-primitives-in-rustc-an-opportunity/6417',
        'https://www.apple.com/newsroom/2019/08/improving-siris-privacy-protections/',
        'https://petapixel.com/2019/08/27/the-sarcophagus-photographing-the-most-radioactive-places-in-chernobyl/',
        'https://www.thedailybeast.com/kristy-meadows-tufts-university-graduate-punished-for-reporting-advisers-fabricated-research-lawsuit',
        'https://blog.plaid.com/how-we-reduced-deployment-times-by-95/',
        'https://thehustle.co/gerald-ratners-billion-dollar-speech', 'http://judy.sourceforge.net/doc/10minutes.htm',
        'https://medium.com/thebigroundtable/the-moralist-ad8159ebe6be',
        'https://www.bloomberg.com/news/articles/2019-08-28/johnson-seeks-parliament-suspension-angering-mps-brexit-update',
        'https://www.thunderbird.net/en-US/thunderbird/68.0/releasenotes/',
        'https://www.bloomberg.com/news/articles/2019-08-28/france-is-still-cleaning-up-marie-curie-s-nuclear-waste',
        'https://www.schneier.com/blog/archives/2019/08/the_myth_of_con.html',
        'https://hub.packtpub.com/rust-is-the-future-of-systems-programming-c-is-the-new-assembly-intel-principal-engineer-josh-triplett/',
        'https://lithub.com/how-to-review-a-novel/', 'https://transfr.io',
        'https://julialang.org/blog/2019/08/release-process',
        'https://heartbeat.fritz.ai/a-2019-guide-to-speech-synthesis-with-deep-learning-630afcafb9dd',
        'https://hire.withgoogle.com/public/jobs/mimirhqcom/view/P_AAAAAADAACHKrbvKW9X25u',
        'https://www.independent.co.uk/news/uk/politics/boris-johnson-suspend-parliament-queen-prorogue-commons-brexit-a9082281.html',
        'https://www.theguardian.com/politics/2019/aug/28/boris-johnson-suspend-parliament-mps-no-deal-brexit',
        'http://hardmath123.github.io/ambigrams.html', 'https://www.commentarymagazine.com/articles/aaargh/',
        'https://www.quantamagazine.org/possible-detection-of-a-black-hole-so-big-it-should-not-exist-20190828/',
        'https://www.cnbc.com/2019/08/28/china-is-reportedly-using-linkedin-to-recruit-spies-overseas.html',
        'https://markmcgranaghan.com/lessons-from-stripe', 'https://blog.michaelbrooks.dev/adding-netlifycms/',
        'https://github.com/michaelkleber/privacy-model',
        'https://www.bighospitality.co.uk/Article/2019/08/28/Vegan-takeaway-orders-quadruple-over-past-two-years',
        'https://www.reuters.com/article/us-gold-swiss-fakes-exclusive/exclusive-fake-branded-bars-slip-dirty-gold-into-world-markets-idUSKCN1VI0DD',
        'https://www.washingtonpost.com/technology/2019/08/28/doorbell-camera-firm-ring-has-partnered-with-police-forces-extending-surveillance-reach/',
        'https://www.bloomberg.com/opinion/articles/2019-08-26/maybe-warren-buffett-is-quietly-warning-us-about-stocks',
        'https://tech.grammarly.com/blog/running-lisp-in-production',
        'https://www.nytimes.com/2019/08/28/magazine/affirmative-action-asian-american-harvard.html',
        'https://www.nytimes.com/2019/08/27/health/sacklers-purdue-pharma-opioid-settlement.html',
        'https://kubernetes.academy/', 'https://tomkiss.net/life/cost_of_owning_a_bmw_i3',
        'https://en.wikipedia.org/wiki/Bulgur',
        'https://jalopnik.com/uber-and-lyft-take-a-lot-more-from-drivers-than-they-sa-1837450373',
        'https://www.fairphone.com/en/special-event/', 'https://news.ycombinator.com/item?id=20818106',
        'https://news.ycombinator.com/item?id=20818750', 'https://jobs.impraise.com/o/elixir-senior-engineer',
        'https://publicdomainreview.org/collections/edgar-allan-poes-the-gold-bug-1843/',
        'http://nautil.us/issue/69/patterns/the-math-that-takes-newton-into-the-quantum-world',
        'https://arstechnica.com/tech-policy/2019/08/youtube-should-stop-recommending-garbage-videos-to-users/',
        'https://www.bbc.com/news/uk-politics-49493632', 'https://www.mozilla.org/en-US/firefox/developer/',
        'http://nextstephq.com', 'https://phys.org/news/2019-08-scientists-harness-bacteria-liquid-crystals.html',
        'https://www.bbc.co.uk/news/uk-politics-49493632',
        'https://github.com/python/cpython/blob/master/Objects/floatobject.c#L965-L972',
        'https://www.sonniesedge.net/posts/react/',
        'https://www.ianvisits.co.uk/blog/2019/08/28/pay-a-visit-to-cambridges-computer-museum/',
        'https://www.theguardian.com/technology/2019/aug/28/australian-who-says-he-invented-bitcoin-ordered-to-hand-over-up-to-5bn',
        'https://www.theparisreview.org/interviews/1887/don-delillo-the-art-of-fiction-no-135-don-delillo',
        'https://wtfutil.com',
        'https://seekingquestions.blogspot.com/2017/03/four-parables-one-lesson-broken-chain.html',
        'https://www.indiehackers.com/post/17788d573f',
        'https://starcity.com/posting/?id=1460a7e6-94a2-4575-81b4-a890e5ee67d1',
        'https://blog.signata.net/military-grade-encryption/',
        'https://www.dropbox.com/s/2ilnmap24jhyj4o/Nutrition_for_Cancer_Prevention.pdf?dl=0',
        'https://www.annualreviews.org/doi/full/10.1146/annurev-economics-080218-030323',
        'https://www.hiroshige.org.uk/Views_Of_Omi/Views_Of_Omi.htm',
        'https://techcrunch.com/2019/08/27/border-deny-entry-united-states-social-media/',
        'https://www.nature.com/articles/d41586-019-02514-7', 'http://www.billporter.info/2013/06/21/led-tetris-tie/',
        'https://www.nytimes.com/2019/08/27/us/harvard-student-ismail-ajjawi.html',
        'https://www.nytimes.com/2019/08/27/world/asia/china-linkedin-spies.html',
        'https://www.smithsonianmag.com/history/government-taste-testers-who-reshaped-americas-diet-180972823/',
        'https://thehill.com/opinion/judiciary/456008-new-york-taxi-regulator-tries-to-put-the-brakes-on-free-speech',
        'http://www.chinafile.com/reporting-opinion/viewpoint/chinas-government-wants-you-think-all-mainlanders-view-hong-kong-same',
        'https://techcrunch.com/2017/12/13/china-cctv-bbc-reporter/',
        'https://www.newsweek.com/fracking-u-s-canada-worldwide-atmospheric-methane-spike-1454205',
        'https://scale.com/careers', 'https://www.laphamsquarterly.org/roundtable/sultan-saladin-fan-club',
        'https://techcrunch.com/2019/08/27/google-will-kill-off-google-hire-in-2020/',
        'https://www.newyorker.com/books/second-read/francoise-sagan-the-great-interrogator-of-morality',
        'https://github.com/entropic-dev/entropic', 'https://github.com/orbitalindex/awesome-space',
        'https://www.bloomberg.com/news/articles/2019-08-22/the-complicated-politics-of-palantir-s-ceo',
        'https://www.thebureauinvestigates.com/stories/2019-07-02/jbs-brazilian-butchers-took-over-the-world', ]

    result = []

    for url in tqdm(url_list):
        result.extend(do_url(url))

    to_csv(result, 'benchmark_compression')


def do_url(url):
    try:
        content = requests.get(url).content
        original_size = sys.getsizeof(content)
    except:
        return []

    results = [
        evaluate(bz2, 9, "bz2", content),
        evaluate(zlib, 9, "zlib", content),
        evaluate(lz4.frame, 16, "lz4", content),
        evaluate(snappy, None, "snappy", content),
        evaluate(blosc, None, "blosc", content),
    ]

    return [{**item, **{
        "original_size": original_size,
        "url": url
    }} for item in results]


def evaluate(module_obj, level, name, content):
    output = {
        "name": name,
        "size_diff": None,
        "compression_time": None,
        "decompression_time": None,
    }

    current_time = time.time()
    if level is not None:
        compressed = module_obj.compress(content, level)
    else:
        compressed = module_obj.compress(content)
    output["compression_time"] = round(time.time() - current_time, 5)

    size_diff = calculate_size_difference(compressed, content)
    output["size_diff"] = size_diff
    output["size_diff_str"] = "%" + str(size_diff)

    current_time = time.time()
    module_obj.decompress(compressed)
    output["decompression_time"] = round(time.time() - current_time, 5)

    return output


def calculate_size_difference(obj1, obj2):
    return round(100 - sys.getsizeof(obj1) / sys.getsizeof(obj2) * 100, 2)


def to_csv(dict_list, file_name):
    field_names = list(dict_list[0].keys())

    with open(file_name + '.csv', 'w', encoding="utf-8") as output_file:
        kwargs = {}

        # Deal with Windows inserting an extra '\r' in line terminators
        if platform.system() == 'Windows':
            kwargs = {'lineterminator': '\n'}

        dict_writer = csv.DictWriter(
            f=output_file,
            fieldnames=field_names,
            quoting=csv.QUOTE_NONNUMERIC,
            **kwargs
        )

        dict_writer.writeheader()
        dict_writer.writerows(dict_list)


if __name__ == '__main__':
    run()
