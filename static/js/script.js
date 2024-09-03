$(document).ready(function() {
    let startPlayer = $('#start-player').text();
    let endPlayer = $('#end-player').text();
    let currentPlayer = startPlayer;
    let pathHistory = [{ player: startPlayer, isRandom: false }];
    let currentPlayerId = '';
    let moveCount = 0;
    let strikes = 0;

    function updateGameInfo() {
        $('#current-player').text(currentPlayer).addClass('animate__animated animate__pulse');
        setTimeout(() => $('#current-player').removeClass('animate__animated animate__pulse'), 1000);
        
        let pathHtml = pathHistory.map(item => {
            let emoji = item.isRandom ? '🌪️' : '✅';
            return `<span class="path-item"><span class="path-item-emoji">${emoji}</span>${item.player}</span>`;
        }).join(' ');
        
        $('#path-history').html(pathHtml);
        updateScoreboard();
    }

    function updateScoreboard() {
        $('#move-count').text(moveCount);
        
        let strikesHtml = '';
        for (let i = 0; i < strikes; i++) {
            strikesHtml += '<div class="strike"></div>';
        }
        $('#strikes').html(strikesHtml);
    }

    function incrementMoveCount() {
        moveCount++;
        updateScoreboard();
    }

    function addStrike() {
        if (strikes < 6) {
            strikes++;
            updateScoreboard();
        }
        if (strikes === 6) {
            gameOver();
        }
    }

    $.getJSON('/autocomplete', { q: startPlayer.split(' (')[0] }, function(data) {
        if (data.length > 0) {
            currentPlayerId = data[0].id;
        }
    });

    $('#player-search').autocomplete({
        source: function(request, response) {
            $.getJSON('/autocomplete', { q: request.term }, function(data) {
                response($.map(data, function(item) {
                    return {
                        label: item.formatted,
                        value: item.id
                    };
                }));
            });
        },
        minLength: 2,
        select: function(event, ui) {
            let selectedPlayerId = ui.item.value;
            let selectedPlayerFormatted = ui.item.label;
            $.ajax({
                url: '/move',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({current_player: currentPlayerId, next_player: selectedPlayerId}),
                success: function(data) {
                    incrementMoveCount(); // Increment move count for each attempt
                    currentPlayer = data.next_player;
                    currentPlayerId = selectedPlayerId;
                    pathHistory.push({ player: currentPlayer, isRandom: !data.success });
                    updateGameInfo();
                    if (data.success) {
                        showPopup('Correct move!');
                    } else {
                        showPopup('Random move!');
                        addStrike(); // Add a strike for random moves
                    }
                    if (currentPlayer === endPlayer) {
                        gameOver();
                    }
                    $('#player-search').val('');
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.error("Error:", textStatus, errorThrown);
                    alert("An error occurred. Please try again.");
                }
            });
        }
    });

    function gameOver() {
        $.ajax({
            url: '/calculate_score',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({path: pathHistory.map(item => item.player.split(' (')[0])}),
            success: function(data) {
                $('#final-score').text(data.score);
                $('#game-over').show().addClass('animate__animated animate__fadeIn');
            }
        });
    }

    $('#copy-result').click(function() {
        let result = `ReceptionPerceptionDaily ${new Date().toISOString().split('T')[0]}\n`;
        result += `Score: ${$('#final-score').text()}\n`;
        result += `Path: ${pathHistory.map(item => item.player).join(' → ')}`;
        navigator.clipboard.writeText(result).then(function() {
            alert('Result copied to clipboard!');
        });
    });

    function showPopup(message) {
        $('body').append(`<div class="popup animate__animated animate__fadeIn">${message}</div>`);
        setTimeout(() => {
            $('.popup').removeClass('animate__fadeIn').addClass('animate__fadeOut');
            setTimeout(() => $('.popup').remove(), 1000);
        }, 2000);
    }

    updateGameInfo();
});