def generate_table(tournament):
    upper_skeleton = '<table style="width: 100%; height: 104px;">\n<tbody>\n<tr style="height: 48px;">\n'
    tournament_info = f'<td style="text-align: center; width: 100%; height: 14px;" colspan="5"><span style="text-align: center;"><strong>{tournament.year}, {tournament.site}</strong></span>\n<span style="text-align: center; color: #808080;">{tournament.name}</span></td></tr>\n'
    headers = '<tr style="height: 24px;">\n<td style="width: 16.8756%; height: 10px;" width="72">M-ce</td>\n<td style="width: 12.969%; height: 10px;" width="72">kat.</td>\n<td style="width: 42.6192%; height: 10px;" width="72">Nazwisko, Imię</td>\n<td style="width: 105.782%; height: 10px;" width="72">R.FIDE</td>\n<td style="width: 1.5625%; height: 10px;" width="72">Pkt.</td>\n</tr>\n'
    bottom_skeleton = '</tbody>\n</table>'

    return f"{upper_skeleton}{tournament_info}{headers}{_generate_group_rows(tournament)}{bottom_skeleton}"

def _format_player_row(player, group):
    place_style = "<strong>" if player.place <= 10 else ""
    place_color = ' style="color: #ff0000;"' if player.place <= 3 else ""
    place = f'<td style="width: 16.8756%; height: 10px;">{place_style}<span{place_color}>{player.place}</span>{place_style}</td>'

    title = f'<td style="width: 12.969%; height: 10px;" width="72">{player.title or ""}</td>'
    name = f'<td class="CR" style="width: 42.6192%; height: 10px;"><a href="{player.url}">{player.name}</a></td>'

    elo_change = f'<strong>(+{player.elo_chg})</strong>' if player.elo_chg >= 0 else f'({player.elo_chg})'
    elo = f'<td class="CRc" style="width: 105.782%; height: 10px;">{player.elo} {elo_change}</td>' if player.elo > 0 else '<td class="CRc" style="width: 105.782%; height: 10px;"></td>'

    points_style = "<strong>" if player.points / group.played_rounds >= 0.5 else ""
    points = f'<td style="width: 1.5625%; height: 10px;">{points_style}{player.points:.1f}/{group.played_rounds:.1f}{points_style}</td>'

    return f'<tr style="height: 24px;">\n{place}\n{title}\n{name}\n{elo}\n{points}\n</tr>'

def _format_group_header(group):
    player_type = "zawodniczek" if group.is_only_female else "zawodników"
    return f'<tr style="background: #C0C0C0;">\n<td style="width: 100%; height: 10px;" colspan="5"><span style="color: #008000;"><a href="{group.url}"><strong>WYNIKI</strong></a> ({group.players_number} {player_type})\n</span></td>\n</tr>'


def _generate_group_rows(tournament):
    return "".join(_format_group_header(group) + "".join(_format_player_row(player, group) for player in group.players) for group in tournament.groups)





