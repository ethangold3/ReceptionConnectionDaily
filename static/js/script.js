$(document).ready(function() {

    $('#reveal-hint').on('click', function() {
        $('#best-path-info').slideToggle();
        $(this).text(function(i, text) {
            return text === "Reveal Hint" ? "Hide Hint" : "Reveal Hint";
        });
    });

    // Show the popup when the page loads
    $('#how-to-play-popup').show();
    // Function to show the popup
    function showHowToPlayPopup() {
        $('#how-to-play-popup').show();
    }

    // Function to show the about popup
    function showAboutPopup() {
        $('#about-popup').show();
    }

    // Function to hide the about popup
    function hideAboutPopup() {
        $('#about-popup').hide();
    }

    // Show about popup when "About" link is clicked
    $('#about-link').click(function(e) {
        e.preventDefault();
        showAboutPopup();
    });

    // Close the about popup when clicking the close button or outside the popup
    $('#about-popup .close').click(hideAboutPopup);

    $(window).click(function(event) {
        if (event.target == document.getElementById('about-popup')) {
            hideAboutPopup();
        }
    });

    // Function to hide the popup
    function hideHowToPlayPopup() {
        $('#how-to-play-popup').hide();
    }

    // Show popup when "How to Play" link is clicked
    $('#how-to-play-link').click(function(e) {
        e.preventDefault(); // Prevent the default anchor behavior
        showHowToPlayPopup();
    });

    // Close the popup when clicking the close button or outside the popup
    $('.close, #start-playing').click(function() {
        $('#how-to-play-popup').hide();
    });

    $(window).click(function(event) {
        if (event.target == document.getElementById('how-to-play-popup')) {
            hideHowToPlayPopup();
        }
    });
    let startPlayer = $('#start-player').text();
    let endPlayer = $('#end-player').text();
    let startPlayerId = $('#start-player').data('player-id');
    let endPlayerId = $('#end-player').data('player-id');
    let currentPlayer = startPlayer;
    let currentPlayerId = startPlayerId;
    let pathHistory = [{ player: startPlayer, id: startPlayerId, isRandom: false }];
    let moveCount = 0;
    let strikes = 0;



    function updateGameInfo() {
        $('#current-player').text(currentPlayer).addClass('animate__animated animate__pulse');
        setTimeout(() => $('#current-player').removeClass('animate__animated animate__pulse'), 1000);
        
        let pathHtml = pathHistory.map((item, index) => {
            let emoji = item.isRandom ? '🌪️' : '🏈';
            let arrow = index < pathHistory.length - 1 ? ' ➔ ' : '';
            return `<span class="path-item">${emoji} ${item.player}${arrow}</span>`;
        }).join('');
        
        $('#path-history').html(pathHtml);
        updateScoreboard();
        updateBestPath();
    }
    function updateBestPath() {
        $.ajax({
            url: '/best_path',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({current_player: currentPlayerId, end_player: endPlayerId}),
            success: function(data) {
                let strength = data.best_path_strength;
                $('#best-path-strength').text(strength.toLocaleString());
                
                // Calculate color based on strength
                let red = Math.min(255, Math.max(0, Math.round(255 * (10000 - strength) / 10000)));
                let green = Math.min(255, Math.max(0, Math.round(255 * strength / 10000)));
                $('#best-path-strength').css('color', `rgb(${red}, ${green}, 0)`);
            }
        });
    }
    function updateStrikes() {
        let filledStrikes = '❌'.repeat(strikes);
        let emptyStrikes = '⚪'.repeat(3 - strikes);
        $('#strike-emojis').text(filledStrikes + emptyStrikes);
        $('#strike-count').text(`${strikes}/3 strikes`);
    }
    function addStrike() {
        console.log("Adding strike. Current strikes:", strikes);
        if (strikes < 3) {
            strikes++;
            updateStrikes();
        }
        if (strikes === 3) {
            gameOver(false);
        }
        console.log("After adding strike. Current strikes:", strikes);
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
                data: JSON.stringify({current_player: currentPlayerId, next_player: selectedPlayerId, path_history: pathHistory}),
                success: function(data) {
                    if (data.success) {
                        // incrementMoveCount(); // Increment move count for each attempt
                        currentPlayer = data.next_player;
                        currentPlayerId = selectedPlayerId;
                        pathHistory.push({ player: currentPlayer, id: currentPlayerId, isRandom: !data.success });
                        updateGameInfo();
                        showPopup('Correct move!');
                        if (currentPlayer === endPlayer) {
                            gameOver(true);;
                        }
                    } else {
                        console.log("Invalid move, adding strike");
                        addStrike();
                        showPopup('Incorrect move! Strike added.');
                    }
                    $('#player-search').val('');
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.error("Error:", textStatus, errorThrown);
                    let errorMessage = jqXHR.responseJSON && jqXHR.responseJSON.error ? jqXHR.responseJSON.error : "An error occurred. Please try again.";
                    showLittleErrorPopup(errorMessage);
                }
            });
        }
    });

    function gameOver(reachedEnd = false) {
        $.ajax({
            url: '/calculate_score',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({path: pathHistory.map(item => item.id)}),
            success: function(data) {
                if (reachedEnd) {
                    showCongratulationsPopup(data.score);
                } else {
                    showGameOverPopup(data.score);
                }
            }
        });
    }

    function showLittleErrorPopup(errorText) {
        const popupId = 'error-popup-' + Date.now();
        const popupHtml = `
            <div id="${popupId}" class="little-error-popup animate__animated animate__fadeIn">
                <span class="error-emoji">❌</span>
                <span class="error-text">${errorText}</span>
            </div>
        `;
        
        $('body').append(popupHtml);
        
        const $popup = $(`#${popupId}`);
        
        // Automatically remove the popup after 2 seconds
        setTimeout(() => {
            $popup.removeClass('animate__fadeIn').addClass('animate__fadeOut');
            setTimeout(() => $popup.remove(), 500);
        }, 2000);
    }

    function showCongratulationsPopup(score) {
        let currentDate = new Date().toISOString().split('T')[0];
        let resultText = `ReceptionConnectionDaily ${currentDate}\n\n`;
        resultText += `🏈 Score: ${score} (lower is better)\n\n`;
        resultText += `Path:\n`;
        resultText += pathHistory.map((item, index) => {
            let emoji = item.isRandom ? '🌪️' : '✅';
            return `${emoji} ${index + 1}. ${item.player}`;
        }).join('\n');
        let popupHtml = `
            <div id="congratulations-popup" class="popup">
                <div class="popup-content">
                    <h2>Congratulations!</h2>
                    <p>You've successfully connected the players!</p>
                    <p>Your score: <span id="final-score">${score}</span></p>
                    <p>Lower scores indicate rarer connections between players. A lower score means you found a more unique path!</p>
                    <div id="result-preview">
                        <h3>Result Preview:</h3>
                        <pre>${resultText}</pre>
                    </div>
                    <button id="copy-result">Copy Result</button>
                    <span id="copy-feedback" style="display: none; color: green; margin-left: 10px;">Copied!</span>
                    <button id="close-popup">Close</button>
                    <p>Come back tomorrow for a new pairing of players!</p>
                </div>
            </div>
        `;
        $('body').append(popupHtml);
        $('#congratulations-popup').show();
    
        $('#copy-result').on('click', function() {
            console.log(resultText);
            navigator.clipboard.writeText(resultText).then(function() {
                $('#copy-feedback').fadeIn().delay(1500).fadeOut();
            }).catch(function(err) {
                console.error('Failed to copy text: ', err);
                alert('Failed to copy text. Please try again.');
            });
        });
    
        $('#close-popup').on('click', function() {
            $('#congratulations-popup').remove();
            console.log('close-popup');
        });
    
        $(window).on('click', function(event) {
            if (event.target.id === 'congratulations-popup') {
                $('#congratulations-popup').remove();
            }
        });
    }
    

function showGameOverPopup(score) {
    let currentDate = new Date().toISOString().split('T')[0];
    let resultText = `ReceptionConnectionDaily ${currentDate}\n\n`;
    resultText += `❌ Failed to connect the players\n`;
    resultText += `🏈 Score: ${score} (lower is better)\n\n`;
    resultText += `Path:\n`;
    resultText += pathHistory.map((item, index) => {
        let emoji = item.isRandom ? '🌪️' : '✅';
        return `${emoji} ${index + 1}. ${item.player}`;
    }).join('\n');
    let popupHtml = `
        <div id="game-over-popup" class="popup">
            <div class="popup-content">
                <h2>Game Over</h2>
                <p>You've reached 3 strikes before connecting the players.</p>
                <p>Your score: <span id="final-score">${score}</span></p>
                <div id="result-preview">
                    <h3>Result Preview:</h3>
                    <pre>${resultText}</pre>
                </div>
                <button id="copy-result">Copy Result</button>
                <span id="copy-feedback" style="display: none; color: green; margin-left: 10px;">Copied!</span>
                <button id="close-popup">Close</button>
                <p>Come back tomorrow for a new pairing of players!</p>
            </div>
        </div>
    `;
    $('body').append(popupHtml);
    $('#game-over-popup').show();

    $('#copy-result').on('click', function() {
        navigator.clipboard.writeText(resultText).then(function() {
            $('#copy-feedback').fadeIn().delay(1500).fadeOut();
        }).catch(function(err) {
            console.error('Failed to copy text: ', err);
            alert('Failed to copy text. Please try again.');
        });
    });

    $('#close-popup').on('click', function() {
        $('#game-over-popup').remove();
    });

    $(window).on('click', function(event) {
        if (event.target.id === 'game-over-popup') {
            $('#game-over-popup').remove();
        }
    });
}

    function showPopup(message) {
        let popupId = 'popup-' + Date.now();
        let popupHtml = `
            <div id="${popupId}" class="popup animate__animated animate__fadeIn">
                ${message}
                <span class="close-popup">&times;</span>
            </div>
        `;
        $('body').append(popupHtml);

        $(`#${popupId} .close-popup`).click(function() {
            $(`#${popupId}`).removeClass('animate__fadeIn').addClass('animate__fadeOut');
            setTimeout(() => $(`#${popupId}`).remove(), 1000);
        });
    }
    updateBestPath();
    updateGameInfo();
    updateStrikes();
});
