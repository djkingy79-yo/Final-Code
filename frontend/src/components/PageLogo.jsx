/**
 * Deb's Criminal Law Appeal Management logo, shown large at the top of
 * every public/info page before any content. Size matches the landing
 * page hero logo (h-[320px] on mobile, h-[400px] on desktop).
 */
const PageLogo = () => (
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
);

export default PageLogo;
