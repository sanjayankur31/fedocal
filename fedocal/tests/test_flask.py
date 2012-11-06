#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
 (c) 2012 - Copyright Pierre-Yves Chibon
 Author: Pierre-Yves Chibon <pingou@pingoured.fr>

 Distributed under License GPLv3 or later
 You can find a copy of this license on the website
 http://www.gnu.org/licenses/gpl.html

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 MA 02110-1301, USA.

 fedocal.model test script
"""

__requires__ = ['SQLAlchemy >= 0.7']
import pkg_resources

import unittest
import sys
import os

from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..', '..'))

import fedocal
import fedocal.fedocallib as fedocallib
from fedocal.tests import Modeltests, DB_PATH
from test_fedocallib import FakeUser


class Flasktests(Modeltests):
    """ Flask application tests. """

    def __setup_db(self):
        """ Add a calendar and some meetings so that we can play with
        something. """
        from test_meeting import Meetingtests
        meeting = Meetingtests('test_init_meeting')
        meeting.session = self.session
        meeting.test_init_meeting()

    def setUp(self):
        """ Set up the environnment, ran before every tests. """
        super(Flasktests, self).setUp()

        fedocal.APP.config['TESTING'] = True
        fedocal.SESSION = fedocallib.create_session(
            'sqlite:///%s' % DB_PATH)
        self.app = fedocal.APP.test_client()

    def test_index_empty(self):
        """ Test the index function. """
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue(
            '<title>   - Fedocal</title>' in rv.data)

    def test_index(self):
        """ Test the index function. """
        self.__setup_db()

        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue(
            '<title> test_calendar  - Fedocal</title>' in rv.data)
        self.assertTrue(' <a href="/test_calendar/">' in rv.data)
        self.assertTrue(' <a href="/test_calendar2/">' in rv.data)
        self.assertTrue(' <a href="/test_calendar4/">' in rv.data)

    def test_calendar(self):
        """ Test the calendar function. """
        self.__setup_db()

        rv = self.app.get('/test_calendar')
        self.assertEqual(rv.status_code, 301)

        rv = self.app.get('/test_calendar', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertTrue(
            '<title> test_calendar  - Fedocal</title>' in rv.data)
        self.assertTrue(' <a href="/test_calendar/">' in rv.data)
        self.assertTrue(' <a href="/test_calendar2/">' in rv.data)
        self.assertTrue(' <a href="/test_calendar4/">' in rv.data)

        rv = self.app.get('/test_calendar2/')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue(
            '<title> test_calendar2  - Fedocal</title>' in rv.data)
        self.assertTrue(' <a href="/test_calendar/">' in rv.data)
        self.assertTrue(' <a href="/test_calendar2/">' in rv.data)
        self.assertTrue(' <a href="/test_calendar4/">' in rv.data)

    def test_calendar_fullday(self):
        """ Test the calendar_fullday function. """
        self.__setup_db()

        today = date.today()
        rv = self.app.get('/test_calendar/%s/%s/%s/' % (today.year,
            today.month, today.day))
        self.assertEqual(rv.status_code, 200)
        self.assertTrue(
            '<title> test_calendar  - Fedocal</title>' in rv.data)
        self.assertTrue(' <a href="/test_calendar/">' in rv.data)
        self.assertTrue(' <a href="/test_calendar2/">' in rv.data)
        self.assertTrue(' <a href="/test_calendar4/">' in rv.data)

        rv = self.app.get('/test_calendar/%s/%s/%s' % (today.year,
            today.month, today.day))
        self.assertEqual(rv.status_code, 301)

        rv = self.app.get('/test_calendar/%s/%s/%s/' % (today.year,
            today.month, today.day), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertTrue(
            '<title> test_calendar  - Fedocal</title>' in rv.data)
        self.assertTrue(' <a href="/test_calendar/">' in rv.data)
        self.assertTrue(' <a href="/test_calendar2/">' in rv.data)
        self.assertTrue(' <a href="/test_calendar4/">' in rv.data)

    def test_ical_out(self):
        """ Test the ical_out function. """
        self.__setup_db()

        today = date.today()
        rv = self.app.get('/ical/test_calendar/')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('BEGIN:VCALENDAR' in rv.data)
        self.assertTrue('SUMMARY:test-meeting2' in rv.data)
        self.assertTrue('DESCRIPTION:This is a test meeting with '\
            'recursion' in rv.data)
        self.assertTrue('ORGANIZER:pingou' in rv.data)
        self.assertEqual(rv.data.count('BEGIN:VEVENT'), 6)
        self.assertEqual(rv.data.count('END:VEVENT'), 6)

    def test_view_meeting(self):
        """ Test the view_meeting function. """
        self.__setup_db()

        rv = self.app.get('/meeting/4/')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('<title> test-meeting-st-1  - Fedocal</title>' \
            in rv.data)
        self.assertTrue('<h4> Meeting: test-meeting-st-1</h4>' \
            in rv.data)
        self.assertTrue('This is a test meeting at the same time' in
            rv.data)

    def test_view_meeting_page(self):
        """ Test the view_meeting_page function. """
        self.__setup_db()

        rv = self.app.get('/meeting/4/1/')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('<title> test-meeting-st-1  - Fedocal</title>' \
            in rv.data)
        self.assertTrue('<h4> Meeting: test-meeting-st-1</h4>' \
            in rv.data)
        self.assertTrue('This is a test meeting at the same time' in
            rv.data)

        rv = self.app.get('/meeting/4/0/')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('<title> test-meeting-st-1  - Fedocal</title>' \
            not in rv.data)
        self.assertTrue('<h4> Meeting: test-meeting-st-1</h4>' \
            in rv.data)
        self.assertTrue('This is a test meeting at the same time' in
            rv.data)


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(Flasktests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)