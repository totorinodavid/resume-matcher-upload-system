import {getRequestConfig} from 'next-intl/server';
 
export default getRequestConfig(async () => {
  // Provide a static locale, fetch a user-specific locale, or
  // read the locale from the headers/path also works
  const locale = 'en';
 
  return {
    locale,
    messages: (await import(`./messages/${locale}.json`)).default
  };
});
