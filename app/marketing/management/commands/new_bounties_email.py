'''
    Copyright (C) 2017 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

'''
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Bounty
from marketing.mails import new_bounty
from marketing.models import EmailSubscriber


class Command(BaseCommand):

    help = 'sends new_bounty _emails'

    def handle(self, *args, **options):
        if settings.DEBUG:
            print("not active in non prod environments")
            return
        hours_back = 24
        eses = EmailSubscriber.objects.filter(active=True)
        print("got {} emails".format(eses.count()))
        for es in eses:
            try:
                keywords = es.keywords
                if not keywords:
                    continue
                to_email = es.email
                bounties_pks = []
                for keyword in keywords:
                    for bounty in Bounty.objects.filter(
                        network='mainnet',
                        web3_created__gt=(timezone.now() - timezone.timedelta(hours=hours_back)),
                        current_bounty=True,
                        metadata__icontains=keyword,
                        ):
                            bounties_pks.append(bounty.pk)
                bounties = Bounty.objects.filter(pk__in=bounties_pks)
                #print("{}/{}: got {} bounties".format(to_email, keywords, bounties.count()))
                if bounties.count():
                    print(f"sent to {to_email}")
                    new_bounty(bounties, [to_email])
            except Exception as e:
                logging.exception(e)
                print(e)
