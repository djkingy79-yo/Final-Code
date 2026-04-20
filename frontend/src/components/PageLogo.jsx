/**
 * Deb's Criminal Law Appeal Management logo, shown large at the top of
 * every public/info page before any content. Size matches the landing
 * page hero logo (h-[320px] on mobile, h-[400px] on desktop). Includes
 * a "Founded by Deb King" attribution caption underneath for consistent
 * authorship visibility across every page (and SEO signal).
 */
const PageLogo = () => (
  <>
    <div
      className="max-w-4xl mx-auto px-6 pt-6 pb-2 flex justify-center"
      data-testid="page-logo-top"
    >
      <img
        src="/logo.png"
        alt="Criminal Law Appeal Case Management — Founded by Deb King"
        className="w-auto h-[320px] sm:h-[400px] object-contain"
      />
    </div>
    <p
      className="text-red-600 font-semibold text-xs uppercase tracking-widest text-center pb-4"
      data-testid="page-logo-founder-caption"
    >
      Founded by Deb King
    </p>
  </>
);

export default PageLogo;

