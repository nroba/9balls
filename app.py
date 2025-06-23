from flask import Flask, render_template, request, redirect, url_for, send_file
import io
import csv
import matplotlib.pyplot as plt

app = Flask(__name__)

# メモリ保持の対戦記録
matches = []

@app.route('/', methods=['GET', 'HEAD'])
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    player1 = request.form['player1']
    player2 = request.form['player2']
    game_type = request.form['game_type']
    date = request.form['date']
    score1 = int(request.form['score1'])
    score2 = int(request.form['score2'])

    # 勝者の自動判定
    if score1 > score2:
        winner = player1
    elif score2 > score1:
        winner = player2
    else:
        winner = '引き分け'

    # 得点差（絶対値）
    point_diff = abs(score1 - score2)

    matches.append({
        'player1': player1,
        'player2': player2,
        'game_type': game_type,
        'winner': winner,
        'date': date,
        'score1': score1,
        'score2': score2,
        'point_diff': point_diff
    })

    return redirect(url_for('show_matches'))

@app.route('/matches')
def show_matches():
    return render_template('matches.html', matches=matches)

@app.route('/download')
def download_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['日付', 'プレイヤー1', '得点1', 'プレイヤー2', '得点2', '得点差', '種目', '勝者'])

    for m in matches:
        writer.writerow([
            m['date'], m['player1'], m['score1'],
            m['player2'], m['score2'],
            m['point_diff'], m['game_type'], m['winner']
        ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='match_records.csv'
    )

@app.route('/stats')
def show_stats():
    stats = {}
    for match in matches:
        for player_key, score_key in [('player1', 'score1'), ('player2', 'score2')]:
            name = match[player_key]
            score = int(match[score_key])
            win = match['winner'] == name
            if name not in stats:
                stats[name] = {'games': 0, 'total_score': 0, 'wins': 0}
            stats[name]['games'] += 1
            stats[name]['total_score'] += score
            stats[name]['wins'] += int(win)

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
