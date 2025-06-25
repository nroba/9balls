from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import io
import csv
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///matches.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)
    shop = db.Column(db.String)
    games = db.Column(db.Integer)
    player1 = db.Column(db.String)
    player2 = db.Column(db.String)
    score1 = db.Column(db.Integer)
    score2 = db.Column(db.Integer)
    ace1 = db.Column(db.Integer)
    ace2 = db.Column(db.Integer)
    cue1 = db.Column(db.String)
    cue2 = db.Column(db.String)
    game_type = db.Column(db.String)
    winner = db.Column(db.String)
    point_diff = db.Column(db.Integer)
    comment = db.Column(db.String)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    shop_list = sorted(set([m.shop for m in Match.query.with_entities(Match.shop).distinct() if m.shop]))
    player_list = sorted(set(
        [m.player1 for m in Match.query.with_entities(Match.player1).distinct()] +
        [m.player2 for m in Match.query.with_entities(Match.player2).distinct()]
    ))
    return render_template('index.html', shop_list=shop_list, player_list=player_list)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form
    score1 = int(data['score1'])
    score2 = int(data['score2'])

    if score1 > score2:
        winner = data['player1']
    elif score2 > score1:
        winner = data['player2']
    else:
        winner = '引き分け'

    match = Match(
        date=data['date'],
        shop=data['shop'],
        games=int(data['games']),
        player1=data['player1'],
        player2=data['player2'],
        score1=score1,
        score2=score2,
        ace1=int(data['ace1']),
        ace2=int(data['ace2']),
        cue1=data['cue1'],
        cue2=data['cue2'],
        game_type=data['game_type'],
        winner=winner,
        point_diff=abs(score1 - score2),
        comment=data.get('comment', '')
    )
    db.session.add(match)
    db.session.commit()
    return redirect(url_for('show_matches'))

@app.route('/matches')
def show_matches():
    matches = Match.query.order_by(Match.id.desc()).all()
    return render_template('matches.html', matches=matches)

@app.route('/download')
def download_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['日付', '店舗名', 'プレイヤー1', '得点1', 'エース1', 'キュー1',
                     'プレイヤー2', '得点2', 'エース2', 'キュー2',
                     '得点差', 'ゲーム数', '種目', '勝者', 'コメント'])

    for m in Match.query.order_by(Match.id).all():
        writer.writerow([
            m.date, m.shop, m.player1, m.score1, m.ace1, m.cue1,
            m.player2, m.score2, m.ace2, m.cue2,
            m.point_diff, m.games, m.game_type, m.winner, m.comment
        ])

    bom = '\ufeff'
    encoded_csv = bom + output.getvalue()

    return send_file(
        io.BytesIO(encoded_csv.encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='match_records.csv'
    )

@app.route('/stats')
def show_stats():
    stats = {}
    matches = Match.query.all()
    for m in matches:
        for name, score, is_winner in [
            (m.player1, m.score1, m.winner == m.player1),
            (m.player2, m.score2, m.winner == m.player2),
        ]:
            if name not in stats:
                stats[name] = {'games': 0, 'total_score': 0, 'wins': 0}
            stats[name]['games'] += 1
            stats[name]['total_score'] += score
            stats[name]['wins'] += int(is_winner)

    players = list(stats.keys())
    avg_scores = [stats[p]['total_score'] / stats[p]['games'] for p in players]
    win_rates = [100 * stats[p]['wins'] / stats[p]['games'] for p in players]

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(players, avg_scores, label='平均得点', alpha=0.6)
    ax1.set_ylabel('平均得点')
    ax1.set_xlabel('プレイヤー')

    ax2 = ax1.twinx()
    ax2.plot(players, win_rates, color='red', marker='o', label='勝率')
    ax2.set_ylabel('勝率（%）')

    plt.title('平均得点と勝率')
    fig.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)

    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
