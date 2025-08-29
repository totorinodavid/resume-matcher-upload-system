import {getRequestConfig} from 'next-intl/server';
import {notFound} from 'next/navigation';
import {locales} from './i18n.config';
 
// Can be imported from a shared config
const localesList = locales;
 
export default getRequestConfig(async ({locale}) => {
  // Validate that the incoming `locale` parameter is valid
  if (!localesList.includes(locale as any)) notFound();
 
  return {
    messages: (await import(`./messages/${locale}.json`)).default
  };
});
