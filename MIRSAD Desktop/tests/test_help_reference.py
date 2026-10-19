"""Manual contracts and independent expected values used in the equation guide."""
import html,json,re,sys,unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
import help_formulas as manual
from mirsad_desktop import science as s


class EquationManualTests(unittest.TestCase):
    def test_every_field_has_a_specific_name_period_unit_and_operation(self):
        count=0
        for module in manual.MODULES:
            for lang in ('ar','en'):
                titles=[]
                for field in manual.calculation_fields(module.name):
                    info=manual.field_reference(module.name,field,lang=='ar')
                    self.assertEqual(set(info),{'title','period','unit','calculation'})
                    self.assertTrue(all(isinstance(v,str) and v.strip() for v in info.values()),field)
                    self.assertNotIn('indicated period',info['calculation'])
                    self.assertNotIn('الشهر، أو',info['calculation'])
                    titles.append(info['title'])
                    if lang=='en':count+=1
                self.assertEqual(len(titles),len(set(titles)),module.name)
        self.assertEqual(count,521)
        with self.assertRaises(ValueError):manual.field_reference('Temperature','T_Unknown_Statistic',False)
        with self.assertRaises(ValueError):manual.field_reference('Temperature','T_Unknown_Mean',False)

    def test_pet_names_separate_month_season_year_and_two_kinds_of_range(self):
        def info(field,ar=False):return manual.field_reference('Evapotranspiration',field,ar)
        self.assertEqual(info('ET_Annual_Mean')['title'],'Annual mean potential evapotranspiration')
        self.assertIn('المتوسط السنوي',info('ET_Annual_Mean',True)['title'])
        self.assertEqual(info('ET_Annual_Mean')['unit'],'mm/year')
        self.assertIn('rather than dividing',info('ET_Annual_Mean')['calculation'])
        self.assertEqual(info('ET_March_Mean')['unit'],'mm/month')
        self.assertIn('مارس',info('ET_March_Mean',True)['title'])
        self.assertIn('Hargreaves',info('ET_March_Mean')['calculation'])
        self.assertIn('31 days',info('ET_March_Mean')['calculation'])
        self.assertIn('28.25 days',info('ET_February_Mean')['calculation'])
        self.assertIn('30 days',info('ET_April_Mean')['calculation'])
        self.assertNotIn('February',info('ET_April_Mean')['calculation'])
        self.assertEqual(info('ET_Summer_Mean')['period'],'Summer (June, July, August)')
        self.assertEqual(info('ET_Summer_Mean')['unit'],'mm/season')
        self.assertIn('Requires all 3 months',info('ET_Summer_Mean')['calculation'])
        self.assertEqual(info('ET_Annual_Range')['title'],'Annual range of potential evapotranspiration')
        self.assertEqual(info('ET_Annual_Range')['unit'],'mm/month')
        self.assertIn('not yearly totals',info('ET_Annual_Range')['calculation'])
        self.assertIn('actual calendar days',info('ET_March_Range')['calculation'])
        self.assertIn('two valid years',info('ET_March_Range')['calculation'])

    def test_special_statistics_have_correct_names_and_units(self):
        cases=[('Relative Humidity','RH_Annual_Range','percentage points','Annual range'),
               ('Cloud Cover','Cld_March_Range','percentage points','March interannual range'),
               ('Solar Radiation','Sol_Annual_Mean','kWh/m²/day','Annual mean'),
               ('Solar Radiation','Sol_Annual_Total','kWh/m²/year','Mean annual total'),
               ('Wind','W_Dir_Winter_Mean','°','Winter mean wind direction'),
               ('Heat Index','HI_Winter_Mean','°C','Winter mean Humidex'),
               ('UNEP Aridity','UNEP_Aridity_Annual','dimensionless ratio','Annual UNEP'),
               ('Dry Months','Dry_Months_Count','months (0–12)','Number of dry months')]
        for module,key,unit,title in cases:
            info=manual.field_reference(module,key,False)
            self.assertEqual(info['unit'],unit)
            self.assertIn(title,info['title'])
        for module,key in [('Temperature','T_Annual_Range'),('Precipitation','R_Annual_Range')]:
            self.assertNotIn('Rothfusz',manual.field_rule(module,key,False))
        self.assertIn('not a month number',manual.field_rule('Wind','W_Spd_Annual_Max_Month',False))
        self.assertIn('T2M_MAX',manual.field_rule('Temperature','T_Annual_Max_Mean',False))

    def test_trend_anomaly_and_month_summary_are_distinct(self):
        info=manual.field_reference('Trends & Anomalies','R_March_Trend_Decade',False)
        self.assertEqual(info['unit'],'mm/decade (10 years)')
        self.assertIn('March rainfall total',info['calculation'])
        self.assertIn('8 valid years',info['calculation'])
        info=manual.field_reference('Trends & Anomalies','R_Anom_Summer_Pct',False)
        self.assertEqual(info['unit'],'%')
        self.assertIn('June, July, August',info['period'])
        self.assertIn('1991–2020',info['calculation'])
        self.assertIn('5 mm',info['calculation'])
        info=manual.field_reference('Trends & Anomalies','T_Anom_Month',False)
        self.assertIn('monthly anomalies',info['title'])
        self.assertIn('T_Anom_March',info['calculation'])
        self.assertIn('not the annual',info['calculation'])

    def test_annual_rain_mean_is_not_monthly_mean_or_interannual_range(self):
        rain={(year,month):value for year,value in [(2023,50.),(2024,100.)] for month in range(1,13)}
        fields=s.compute_point_fields({'PRECTOTCORR':rain},[2023,2024],['Precipitation'],'Monthly',precip_totals=True,gap_method='none',monthly_ranges=True)
        self.assertEqual(fields['R_Annual_Mean'],900.) # mean(600, 1200)
        self.assertEqual(fields['R_March_Mean'],75.)
        self.assertEqual(fields['R_Annual_Range'],0.) # all calendar-month climatologies =75
        self.assertEqual(fields['R_March_Range'],50.) # 100-50, across years

    def test_review_and_every_module_field_is_explained_in_both_languages(self):
        manual.check_review()
        index=json.loads((ROOT/'assets/help_index.json').read_text(encoding='utf-8'))
        sections={t['id']:t for t in index['sections']}
        spec=json.loads((manual.SOURCE/'formulas.json').read_text(encoding='utf-8'))
        self.assertEqual(len(spec['entries']),19)
        for entry in spec['entries']:
            for lang in ('ar','en'):
                body=sections[entry['id']][lang+'_body']
                for key in ('steps','limits','example'):
                    self.assertIn(html.escape(entry[key+'_'+lang]),body)
                for field in manual.calculation_fields(entry['module']):
                    self.assertIn('<code>'+field+'</code>',body)
                    self.assertTrue(manual.field_rule(entry['module'],field,lang=='ar'))
                    for value in manual.field_reference(entry['module'],field,lang=='ar').values():
                        self.assertIn(html.escape(value),body)

    def test_internal_topic_links_and_legacy_launcher_allowlist(self):
        sys.path.insert(0,str(ROOT.parent))
        from utils.help_viewer import TOPICS,help_path
        index=json.loads((ROOT/'assets/help_index.json').read_text(encoding='utf-8'))
        ids={t['id'] for t in index['sections']}
        self.assertEqual(ids,set(TOPICS))
        for topic in index['sections']:
            for lang in ('ar','en'):
                for target in re.findall(r'href="#([a-z0-9_-]+)"',topic[lang+'_body']):
                    # Parameter tables contain local section anchors as well.
                    self.assertTrue(target in ids or ('id="'+target+'"') in topic[lang+'_body'] or ('name="'+target+'"') in topic[lang+'_body'],target)
        with self.assertRaises(ValueError):help_path('../outside')

    def test_rain_leap_year_and_missing_is_not_zero(self):
        self.assertEqual(s.monthly_precip_total_from_rate(2,2024,2),58.)
        self.assertIsNone(s.monthly_precip_total_from_rate(None,2024,2))
        monthly={(2024,m):50. for m in range(1,13)}
        full=s.compute_point_fields({'PRECTOTCORR':monthly},[2024],['Precipitation'],'Monthly',precip_totals=True,gap_method='none')
        self.assertEqual(full['R_Annual_Mean'],600.)
        del monthly[(2024,2)]
        incomplete=s.compute_point_fields({'PRECTOTCORR':monthly},[2024],['Precipitation'],'Monthly',precip_totals=True,gap_method='none')
        self.assertIsNone(incomplete['R_Annual_Mean'])

    def test_drought_examples_and_strict_dry_threshold(self):
        def months(value):return {(2024,m):value for m in range(1,13)}
        # Given Ra=10 mm/day, Jan PET is the hand-calculated 85.2278 mm.
        with patch.object(s,'extraterrestrial_radiation_ra',return_value=10.):
            result=s.compute_drought_fields(months(20),months(25),months(15),months(50),lat=0)
        self.assertEqual(result['ET_January_Mean'],85.2)
        self.assertEqual(result['DM_Aridity_Annual'],20.)
        self.assertEqual(result['Dry_Months_Count'],0)
        self.assertLess(result['Water_Deficit_Annual'],0)
        self.assertEqual(s.compute_drought_fields(months(20),months(25),months(15),months(10))['Dry_Months_Count'],12)
        self.assertEqual(s.compute_drought_fields(months(20),months(25),months(15),months(40))['Dry_Months_Count'],0)
        missing=months(50);missing[(2024,2)]=None
        result=s.compute_drought_fields(months(20),months(25),months(15),missing)
        for field in ('DM_Aridity_Annual','UNEP_Aridity_Annual','Water_Deficit_Annual','Dry_Months_Count'):
            self.assertIsNone(result[field])
        self.assertIsNotNone(result['PET_Hargreaves_Annual'])

    def test_circular_wind_and_solar_energy_calendar(self):
        self.assertAlmostEqual(s.circular_mean_deg([350,10])%360,0.,places=7)
        self.assertIsNone(s.circular_mean_deg([90,270]))
        result=s.compute_solar_fields({(2024,m):18. for m in range(1,13)},[2024])
        self.assertEqual(result['Sol_Annual_Mean'],5.)
        self.assertEqual(result['Sol_Annual_Total'],1830.)

    def test_winter_humidex_is_distinct_from_monthly_rothfusz(self):
        t={m:20. for m in range(1,13)};rh={m:60. for m in range(1,13)}
        result=s.compute_thermal_stress_fields(t,rh)
        self.assertEqual(result['HI_Annual_Mean'],20.)
        self.assertEqual(result['HI_January_Mean'],20.)
        self.assertAlmostEqual(result['HI_Winter_Mean'],22.23,places=2)
        self.assertEqual(s.windchill_c(20,3),20.)

    def test_actual_year_trend_and_minimum_coverage(self):
        series={year:10.+year-2000 for year in range(2000,2008)}
        self.assertAlmostEqual(s._lin_trend_per_decade(series),10.)
        del series[2001]
        self.assertIsNone(s._lin_trend_per_decade(series))
        baseline={year:100. for year in range(1991,2021)}
        baseline.update({year:120. for year in range(2021,2031)})
        self.assertEqual(s._recent_minus_baseline(baseline),(120.,100.))
        monthly={(y,m):v/12. for y,v in baseline.items() for m in range(1,13)}
        result=s.compute_point_fields({'PRECTOTCORR':monthly},sorted(baseline),['Trends & Anomalies'],'Monthly',precip_totals=True,gap_method='none')
        self.assertEqual(result['R_Annual_Anom'],20.)
        self.assertEqual(result['R_Annual_Anom_Pct'],20.)

    def test_absolute_vs_delta_temperature_units(self):
        fields={'T_Annual_Mean':20.,'T_Annual_Range':8.,'T_Annual_Trend_Decade':2.}
        result=s.convert_fields_to_user_units(fields,unit_temp='Fahrenheit')
        self.assertEqual(result['T_Annual_Mean'],68.)
        self.assertEqual(result['T_Annual_Range'],14.4)
        self.assertEqual(result['T_Annual_Trend_Decade'],3.6)


if __name__=='__main__':unittest.main()
