import { Component, OnInit } from '@angular/core';
import { Chess } from 'chess.js';
import { NgFor, NgIf, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-chess-board',
  standalone: true,
  imports: [NgFor, NgIf, FormsModule, CommonModule],
  templateUrl: './chess-board.component.html',
  styleUrls: ['./chess-board.component.scss']
})
export class ChessBoardComponent implements OnInit {
  game = new Chess();
  board: ({ type: string, color: string } | null)[][] = [];
  chatHistory: { role: 'user' | 'assistant'; content: string }[] = [];

  selectedSquare: string | null = null;
  moveCommentary: string = '';
  isPlayerTurn = true;

  chatInput: string = '';
  chatResponse: string = '';

  ngOnInit() {
    this.renderBoard();
  }

  renderBoard() {
    const boardState = this.game.board();
    this.board = boardState.map(row =>
      row.map(piece => piece ? { type: piece.type, color: piece.color } : null)
    );
  }

  getPieceSymbol(square: { type: string, color: string } | null): string {
    if (!square) return '';

    const unicodePieces: { [key: string]: string } = {
      wp: '♙',
      wn: '♘',
      wb: '♗',
      wr: '♖',
      wq: '♕',
      wk: '♔',
      bp: '♟',
      bn: '♞',
      bb: '♝',
      br: '♜',
      bq: '♛',
      bk: '♚',
    };

    return unicodePieces[square.color + square.type] || '';
  }

  onSquareClick(row: number, col: number) {
  if (!this.isPlayerTurn || this.game.isGameOver()) {
    if (this.game.isGameOver()) {
      this.moveCommentary = 'Game over: ' + (this.game.isCheckmate() ? 'Checkmate' : 'Draw');
    }
    return;
  }

  const square = String.fromCharCode(97 + col) + (8 - row);

  if (!this.selectedSquare) {
    this.selectedSquare = square;
    return;
  }

  const move = { from: this.selectedSquare, to: square };
  const fenBeforeMove = this.game.fen();
  const humanPieceColor = this.game.turn();
  const allLegalMoves = this.game.moves({ verbose: true });
  
  const legalMoves = allLegalMoves
    .filter(move => {
      const piece = this.game.get(move.from);
      return piece && piece.color === humanPieceColor;
    })
    .map(move => ({
      from: move.from,
      to: move.to,
      san: move.san,
      promotion: move.promotion || null
    }));

  const result = this.game.move(move);

  if (result) {
    this.selectedSquare = null;
    this.renderBoard();
    this.isPlayerTurn = false;

    
    const aiPieceColor = this.game.turn();
    const uciMove = result.from + result.to + (result.promotion || '');
    
    this.sendMoveToLLM(fenBeforeMove, uciMove, legalMoves, humanPieceColor, aiPieceColor);
  } else {
    this.selectedSquare = null;
  }
}

  sendMoveToLLM(fen: string, playerMove: string, legalMoves: { from: string; to: string; san: string; promotion: string | null }[], humanPieceColor: string, aiPieceColor: string) {
  if (!this.validateFen(fen)) {
    this.moveCommentary = 'Error: Invalid board state.';
    this.isPlayerTurn = true;
    return;
  }

  const previousFen = this.game.fen();
  fetch('http://localhost:8000/api/llm-move', {
    method: 'POST',
    body: JSON.stringify({
      fen,
      playerMove,
      legalMoves,
      humanPieceColor,
      aiPieceColor    
    }),
    headers: { 'Content-Type': 'application/json' }
  })
    .then(res => res.json())
    .then((data: { llmMove?: string; commentary: string }) => {
      if (data.llmMove && data.llmMove !== 'none') {
        const from = data.llmMove.slice(0, 2);
        const to = data.llmMove.slice(2, 4);
        const promotion = data.llmMove.length > 4 ? data.llmMove[4] : undefined;

        const moveResult = this.game.move({ from, to, promotion });
        if (moveResult) {
          this.renderBoard();
          this.moveCommentary = data.commentary;
        } else {
          this.moveCommentary = `LLM suggested invalid move: ${data.llmMove}`;
          this.game.load(previousFen);
          this.renderBoard();
        }
      } else {
        this.moveCommentary = data.commentary || 'LLM returned no move.';
      }
      this.isPlayerTurn = true;
    })
    .catch(err => {
      console.error('Error fetching LLM move:', err);
      this.moveCommentary = 'Error communicating with LLM.';
      this.game.load(previousFen);
      this.renderBoard();
      this.isPlayerTurn = true;
    });
}

  validateFen(fen: string): boolean {
    try {
      const tempGame = new Chess(fen);
      return tempGame.fen() === fen;
    } catch (e) {
      console.error('Invalid FEN:', fen);
      return false;
    }
  }

  sendChat() {
    if (!this.chatInput.trim()) return;

    this.chatHistory.push({ role: 'user', content: this.chatInput });

    fetch('http://localhost:8000/api/llm-chat', {
      method: 'POST',
      body: JSON.stringify({
        fen: this.game.fen(),
        question: this.chatInput,
        history: this.chatHistory
      }),
      headers: { 'Content-Type': 'application/json' }
    })
      .then(res => res.json())
      .then(data => {
        const reply = data.response || 'No reply.';
        this.chatResponse = reply;
        this.chatHistory.push({ role: 'assistant', content: reply });
        this.chatInput = '';
      });
  }
}